import pytest

from cloudflare_exporter.metrics import (
    CloudflareCollector,
    FirewallEventEntry,
    FirewallEventMetrics,
    HttpRequestEntry,
    HttpRequestMetrics,
)


@pytest.fixture
def sample_http_metrics_data() -> list[HttpRequestEntry]:
    """Create sample HTTP metrics data for testing."""
    return [
        {
            "dimensions": {
                "clientCountryName": "United States",
                "edgeResponseStatus": 200,
            },
            "sum": {
                "requests": 2,
                "bytes": 4,
                "cachedRequests": 1,
                "cachedBytes": 2,
            },
        }
    ]


@pytest.fixture
def sample_firewall_metrics_data() -> list[FirewallEventEntry]:
    """Create sample firewall metrics data for testing."""
    return [
        {
            "count": 100,
            "dimensions": {
                "action": "log",
                "ruleId": "edf8c37cc81747d382690b3c77e82ce4",
                "source": "firewallManaged",
            },
        }
    ]


@pytest.fixture
def collector() -> CloudflareCollector:
    """Fixture providing a CloudflareCollector instance."""
    return CloudflareCollector()


def test_collector_initialization(collector: CloudflareCollector) -> None:
    """Test collector initialization."""
    assert collector.http_metrics_data == []
    assert collector.firewall_metrics_data == []
    assert collector._lock is not None


# Test constants
EXPECTED_METRIC_COUNT = 9
TEST_REQUEST_COUNT = 100
TEST_BYTES_TOTAL = 1024000
TEST_CACHED_REQUESTS = 75
TEST_CACHED_BYTES = 768000
TEST_FIREWALL_COUNT = 100
TARGET_HTTP_METRICS_COUNT = 5  # Number of HTTP metrics after thread test
TARGET_FIREWALL_METRICS_COUNT = 0  # No firewall metrics in thread test


def test_update_metrics(
    collector: CloudflareCollector,
    sample_http_metrics_data: list[HttpRequestEntry],
) -> None:
    """Test updating metrics with sample data."""
    timestamp = "2024-03-08T12:00:00Z"
    zone_name = "test-domain-123.example.com"

    # Update sample data to match expected format
    sample_http_metrics_data[0]["sum"].update(
        {
            "requests": 100,
            "bytes": 1024000,
            "cachedRequests": 75,
            "cachedBytes": 768000,
        }
    )

    collector._update_metrics(
        sample_http_metrics_data,  # type: ignore[arg-type]
        zone_name,
        timestamp,
        "account_name",
        "account_id",
        100.0,
        50.0,
        50.0,
    )

    # Convert generator to list for testing
    metrics = list(collector.collect())
    assert len(metrics) == EXPECTED_METRIC_COUNT

    # Verify metric names
    metric_names = {m.name for m in metrics}
    expected_names = {
        "cloudflare_requests_total",
        "cloudflare_bytes_total",
        "cloudflare_cached_requests_total",
        "cloudflare_cached_bytes_total",
        "cloudflare_scrape_errors_total",
        "cloudflare_enterprise_zone_quota_max",
        "cloudflare_enterprise_zone_quota_available",
        "cloudflare_enterprise_zone_quota_current",
        "cloudflare_firewall_events_total",
    }
    assert metric_names == expected_names


def test_multiple_metrics(collector: CloudflareCollector) -> None:
    """Test handling multiple metrics entries."""
    timestamp = "2024-03-08T12:00:00Z"
    zone_name = "test-domain-123.example.com"
    data: list[HttpRequestEntry | FirewallEventEntry] = [
        {
            "dimensions": {
                "clientCountryName": "United States",
                "edgeResponseStatus": 200,
            },
            "sum": {
                "requests": 100,
                "bytes": 1024000,
                "cachedRequests": 75,
                "cachedBytes": 768000,
            },
        }
    ]
    collector._update_metrics(
        data, zone_name, timestamp, "account_name", "account_id", 100.0, 50.0, 50.0
    )

    metrics = list(collector.collect())
    assert len(metrics) == EXPECTED_METRIC_COUNT


def test_multiple_zones(collector: CloudflareCollector) -> None:
    """Test handling metrics from multiple zones."""
    for index in range(3):
        data: list[HttpRequestEntry | FirewallEventEntry] = [
            {
                "dimensions": {
                    "clientCountryName": f"Country{index}",
                    "edgeResponseStatus": 200,
                },
                "sum": {
                    "requests": 100 + index,
                    "bytes": 1024000 + index,
                    "cachedRequests": 75 + index,
                    "cachedBytes": 768000 + index,
                },
            }
        ]
        collector._update_metrics(
            data,
            f"zone-{index}.example.com",
            "2024-03-08T12:00:00Z",
            "account_name",
            "account_id",
            100.0,
            50.0,
            50.0,
        )

    metrics = list(collector.collect())
    assert len(metrics) == EXPECTED_METRIC_COUNT


def test_collect(
    collector: CloudflareCollector,
    sample_http_metrics_data: list[HttpRequestEntry | FirewallEventEntry],
) -> None:
    """Test collecting metrics for Prometheus."""
    timestamp = "2024-03-08T12:00:00Z"
    zone_name = "example.com"

    metrics_sum: HttpRequestMetrics = {
        "requests": TEST_REQUEST_COUNT,
        "bytes": TEST_BYTES_TOTAL,
        "cachedRequests": TEST_CACHED_REQUESTS,
        "cachedBytes": TEST_CACHED_BYTES,
    }
    sample_http_metrics_data[0]["sum"].update(metrics_sum)  # type: ignore[typeddict-item]

    collector._update_metrics(
        sample_http_metrics_data,
        zone_name,
        timestamp,
        "account_name",
        "account_id",
        100.0,
        50.0,
        50.0,
    )

    metrics = list(collector.collect())
    assert len(metrics) == EXPECTED_METRIC_COUNT

    # Verify metric values
    for metric in metrics:
        if metric.name == "cloudflare_requests_total":
            assert metric.samples[0].value == TEST_REQUEST_COUNT
        elif metric.name == "cloudflare_bytes_total":
            assert metric.samples[0].value == TEST_BYTES_TOTAL
        elif metric.name == "cloudflare_cached_requests_total":
            assert metric.samples[0].value == TEST_CACHED_REQUESTS
        elif metric.name == "cloudflare_cached_bytes_total":
            assert metric.samples[0].value == TEST_CACHED_BYTES
        elif metric.name == "cloudflare_scrape_errors_total":
            assert metric.samples[0].value == 0


def test_thread_safety(collector: CloudflareCollector) -> None:
    """Test thread safety of metrics updates."""
    import threading

    def update_metrics(index: int) -> None:
        data: list[HttpRequestEntry | FirewallEventEntry] = [
            {
                "dimensions": {
                    "clientCountryName": f"Country{index}",
                    "edgeResponseStatus": 200,
                },
                "sum": {
                    "requests": 100 * index,
                    "bytes": 1024 * index,
                    "cachedRequests": 75 * index,
                    "cachedBytes": 768000 * index,
                },
            }
        ]
        collector._update_metrics(
            data,
            f"zone{index}.com",
            "2024-03-08T12:00:00Z",
            "account_name",
            "account_id",
            100.0,
            50.0,
            50.0,
        )

    threads = []
    for i in range(5):
        thread = threading.Thread(target=update_metrics, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Only the last update should be present due to the design
    assert len(collector.http_metrics_data) == TARGET_HTTP_METRICS_COUNT
    assert len(collector.firewall_metrics_data) == TARGET_FIREWALL_METRICS_COUNT


def create_test_http_metric_entry(
    country: str = "United States",
    status: int = 200,
    requests: int = 0,
    bytes_: int = 0,
    cached_requests: int = 0,
    cached_bytes: int = 0,
) -> HttpRequestEntry | FirewallEventEntry:
    """Helper function to create test HTTP metric entries."""
    return {
        "dimensions": {
            "clientCountryName": country,
            "edgeResponseStatus": status,
        },
        "sum": {
            "requests": requests,
            "bytes": bytes_,
            "cachedRequests": cached_requests,
            "cachedBytes": cached_bytes,
        },
    }


def create_test_firewall_metric_entry(
    action: str = "block",
    rule_id: str = "rule1",
    source: str = "waf",
    count: int = 0,
) -> FirewallEventEntry:
    """Helper function to create test firewall metric entries."""
    return {
        "dimensions": {
            "action": action,
            "ruleId": rule_id,
            "source": source,
        },
        "count": count,
    }


def test_update_firewall_metrics(
    collector: CloudflareCollector,
    sample_firewall_metrics_data: list[HttpRequestEntry | FirewallEventEntry],
) -> None:
    """Test updating firewall metrics."""
    timestamp = "2024-03-08T12:00:00Z"
    zone_name = "test-domain-123.example.com"

    collector._update_metrics(
        sample_firewall_metrics_data,
        zone_name,
        timestamp,
        "account_name",
        "account_id",
        100.0,
        50.0,
        50.0,
    )

    metrics = list(collector.collect())
    assert len(metrics) == EXPECTED_METRIC_COUNT

    # Verify firewall metrics specifically
    firewall_metrics = [
        m for m in metrics if m.name == "cloudflare_firewall_events_total"
    ]
    assert len(firewall_metrics) == 1
    assert firewall_metrics[0].samples[0].value == TEST_FIREWALL_COUNT


def test_combined_http_and_firewall_metrics(
    collector: CloudflareCollector,
    sample_http_metrics_data: list[HttpRequestEntry | FirewallEventEntry],
    sample_firewall_metrics_data: list[HttpRequestEntry | FirewallEventEntry],
) -> None:
    """Test collecting both HTTP and firewall metrics together."""
    timestamp = "2024-03-08T12:00:00Z"
    zone_name = "example.com"

    # Prepare HTTP metrics
    http_metrics: HttpRequestMetrics = {
        "requests": TEST_REQUEST_COUNT,
        "bytes": TEST_BYTES_TOTAL,
        "cachedRequests": TEST_CACHED_REQUESTS,
        "cachedBytes": TEST_CACHED_BYTES,
    }
    sample_http_metrics_data[0]["sum"].update(http_metrics)  # type: ignore[typeddict-item]

    # Prepare firewall metrics
    firewall_metrics: FirewallEventMetrics = {"count": TEST_FIREWALL_COUNT}
    sample_firewall_metrics_data[0]["count"] = firewall_metrics["count"]  # type: ignore[typeddict-unknown-key]

    # Update metrics with HTTP data
    collector._update_metrics(
        sample_http_metrics_data,
        zone_name,
        timestamp,
        "account_name",
        "account_id",
        100.0,
        50.0,
        50.0,
    )

    # Update metrics with firewall data
    collector._update_metrics(
        sample_firewall_metrics_data,
        zone_name,
        timestamp,
        "account_name",
        "account_id",
        100.0,
        50.0,
        50.0,
    )

    # Verify all metrics
    metrics = list(collector.collect())
    assert len(metrics) == EXPECTED_METRIC_COUNT

    # Verify HTTP metrics
    for metric in metrics:
        if metric.name == "cloudflare_requests_total":
            assert metric.samples[0].value == TEST_REQUEST_COUNT
        elif metric.name == "cloudflare_bytes_total":
            assert metric.samples[0].value == TEST_BYTES_TOTAL
        elif metric.name == "cloudflare_cached_requests_total":
            assert metric.samples[0].value == TEST_CACHED_REQUESTS
        elif metric.name == "cloudflare_cached_bytes_total":
            assert metric.samples[0].value == TEST_CACHED_BYTES
        elif metric.name == "cloudflare_firewall_events_total":
            assert metric.samples[0].value == TEST_FIREWALL_COUNT
        elif metric.name == "cloudflare_scrape_errors_total":
            assert metric.samples[0].value == 0

    # Verify metric labels
    http_metric = next(m for m in metrics if m.name == "cloudflare_requests_total")
    assert http_metric.samples[0].labels == {
        "zone": zone_name,
        "country": "United States",
        "status": "200",
        "account": "account_name",
        "account_id": "account_id",
    }

    firewall_metric = next(
        m for m in metrics if m.name == "cloudflare_firewall_events_total"
    )
    assert firewall_metric.samples[0].labels == {
        "zone": zone_name,
        "action": "log",
        "rule_id": "edf8c37cc81747d382690b3c77e82ce4",
        "source": "firewallManaged",
        "account": "account_name",
        "account_id": "account_id",
    }
