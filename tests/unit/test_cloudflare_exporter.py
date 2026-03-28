from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
import requests

from cloudflare_exporter.cloudflare_exporter import (
    _buffer_metrics,
    _get_datasets,
    _make_cloudflare_request,
    _process_metrics_data,
    _rounddown_time,
    cloudflare_define_zones,
    cloudflare_fetch_metrics,
)
from cloudflare_exporter.config import CloudflareConfig, CmbRegion
from cloudflare_exporter.metrics import (
    CloudflareCollector,
    FirewallEventEntry,
    HttpRequestEntry,
)

# Add these constants at the top of the file
TEST_REQUEST_COUNT = 100
TEST_FIREWALL_EVENT_COUNT = 50
EDGE_RESPONSE_STATUS = 200
REQUESTS = 100
BYTES = 1024
CACHED_REQUESTS = 50
CACHED_BYTES = 512


@pytest.fixture
def mock_config() -> CloudflareConfig:
    """Fixture providing a mock configuration."""
    return CloudflareConfig(
        api_token="test_token", cmb_region=CmbRegion.GLOBAL, scrape_delay=60
    )


@pytest.fixture
def mock_client() -> MagicMock:
    """Fixture providing a mock Cloudflare client."""
    client = MagicMock()
    zone1 = MagicMock()
    zone1.id = "023e105f4ecef8ad9ca31a8372d0c353"
    zone1.name = "example1.com"

    client.zones.list.return_value.result = [zone1]
    return client


@pytest.fixture
def mock_account() -> MagicMock:
    """Fixture providing a mock Cloudflare account."""
    account = MagicMock()
    account.id = "test_account_id"
    account.name = "test_account"
    account.legacy_flags = {
        "enterprise_zone_quota": {"maximum": 100, "current": 50, "available": 50}
    }
    return account


def test_rounddown_time() -> None:
    """Test rounding down datetime."""
    test_time = datetime(2024, 3, 8, 12, 34, 56, 789, tzinfo=UTC)
    result = _rounddown_time(test_time)
    assert result == "2024-03-08T12:34:00Z"


def test_cloudflare_define_zones_all(
    mock_client: MagicMock, mock_config: CloudflareConfig
) -> None:
    """Test zone definition with no filters."""
    mock_config.zones = None  # Ensure no specific zones set
    mock_config.exclude_zones = None  # Ensure no exclusions
    zones = cloudflare_define_zones(mock_client, mock_config)
    assert zones == ["023e105f4ecef8ad9ca31a8372d0c353"]
    mock_client.zones.list.assert_called_once()


def test_cloudflare_define_zones_specific(
    mock_client: MagicMock, mock_config: CloudflareConfig
) -> None:
    """Test zone definition with specific zones."""
    mock_config.zones = (
        "023e105f4ecef8ad9ca31a8372d0c353,023e105f4ecef8ad9ca31a8372d0c355"
    )
    zones = cloudflare_define_zones(mock_client, mock_config)
    assert zones == [
        "023e105f4ecef8ad9ca31a8372d0c353",
        "023e105f4ecef8ad9ca31a8372d0c355",
    ]
    mock_client.zones.list.assert_not_called()


def test_cloudflare_define_zones_exclude(
    mock_client: MagicMock, mock_config: CloudflareConfig
) -> None:
    """Test zone definition with exclusions."""
    # Set up mock client to return specific zones
    zone1 = MagicMock()
    zone1.id = "023e105f4ecef8ad9ca31a8372d0c353"
    zone2 = MagicMock()
    zone2.id = "023e105f4ecef8ad9ca31a8372d0c354"
    mock_client.zones.list.return_value.result = [zone1, zone2]

    # Configure exclusions
    mock_config.zones = None  # Reset zones to use list from API
    mock_config.exclude_zones = "023e105f4ecef8ad9ca31a8372d0c354"

    zones = cloudflare_define_zones(mock_client, mock_config)
    assert zones == ["023e105f4ecef8ad9ca31a8372d0c353"]


def test_make_cloudflare_request_success() -> None:
    """Test successful API request."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "test"}

    with patch("requests.post", return_value=mock_response):
        result = _make_cloudflare_request(
            "https://api.test", {"Authorization": "Bearer test"}, {"query": "test"}
        )
        assert result == {"data": "test"}


def test_make_cloudflare_request_retry() -> None:
    """Test API request with retries."""
    mock_success = MagicMock()
    mock_success.json.return_value = {"data": "test"}

    with patch(
        "requests.post",
        side_effect=[requests.exceptions.RequestException(), mock_success],
    ):
        result = _make_cloudflare_request(
            "https://api.test", {"Authorization": "Bearer test"}, {"query": "test"}
        )
        assert result == {"data": "test"}


def test_make_cloudflare_request_failure() -> None:
    """Test API request failure after retries."""
    mock_collector = MagicMock()  # Create a mock collector instance
    with (
        patch(
            "requests.post",
            side_effect=requests.exceptions.RequestException("API Error"),
        ),
        patch("cloudflare_exporter.cloudflare_exporter.COLLECTOR", mock_collector),
    ):
        with pytest.raises(Exception) as exc_info:
            _make_cloudflare_request(
                "https://api.test", {"Authorization": "Bearer test"}, {"query": "test"}
            )
        assert "Failed to fetch Cloudflare data after 3 attempts" in str(exc_info.value)
        mock_collector.increment_error_counter.assert_called_once()


@patch("cloudflare_exporter.cloudflare_exporter._get_query")
@patch("cloudflare_exporter.cloudflare_exporter._make_cloudflare_request")
def test_cloudflare_fetch_metrics_success(
    mock_request: MagicMock,
    mock_get_query: MagicMock,
    mock_client: MagicMock,
    mock_config: CloudflareConfig,
    mock_account: MagicMock,
) -> None:
    """Test successful metrics fetch."""
    mock_get_query.return_value = "query { test }"
    mock_request.return_value = {
        "data": {
            "viewer": {
                "zones": [{"httpRequestsOverviewAdaptiveGroups": [{"test": "data"}]}]
            }
        }
    }

    cloudflare_fetch_metrics(mock_account, mock_client, mock_config, ["zone1"])
    assert mock_request.called
    assert mock_get_query.called


@patch("cloudflare_exporter.cloudflare_exporter._get_query")
@patch("cloudflare_exporter.cloudflare_exporter._make_cloudflare_request")
def test_cloudflare_fetch_metrics_error_handling(
    mock_request: MagicMock,
    mock_get_query: MagicMock,
    mock_client: MagicMock,
    mock_config: CloudflareConfig,
    mock_account: MagicMock,
) -> None:
    """Test metrics fetch error handling."""
    mock_get_query.return_value = "query { test }"
    mock_request.return_value = {"errors": [{"message": "Test error"}]}

    # Should not raise exception but log error
    cloudflare_fetch_metrics(mock_account, mock_client, mock_config, ["zone1"])


def test_process_metrics_data_http_requests() -> None:
    """Test processing HTTP request metrics data."""
    raw_data_http = [
        {
            "dimensions": {
                "clientCountryName": "US",
                "edgeResponseStatus": 200,
            },
            "sum": {
                "requests": 100,
                "bytes": 1024,
                "cachedRequests": 50,
                "cachedBytes": 512,
            },
        }
    ]
    processed_http = _process_metrics_data(
        raw_data_http, "httpRequestsOverviewAdaptiveGroups", True
    )
    for item in processed_http:
        assert "dimensions" in item
        assert "sum" in item
        assert item["dimensions"]["clientCountryName"] == "US"  # type: ignore[typeddict-item]
        assert item["dimensions"]["edgeResponseStatus"] == EDGE_RESPONSE_STATUS  # type: ignore[typeddict-item]
        assert item["sum"]["requests"] == REQUESTS  # type: ignore[typeddict-item]
        assert item["sum"]["bytes"] == BYTES  # type: ignore[typeddict-item]
        assert item["sum"]["cachedRequests"] == CACHED_REQUESTS  # type: ignore[typeddict-item]
        assert item["sum"]["cachedBytes"] == CACHED_BYTES  # type: ignore[typeddict-item]


def test_process_metrics_data_firewall_events() -> None:
    """Test processing firewall event metrics data."""
    raw_data_firewall = [
        {
            "dimensions": {
                "action": "block",
                "ruleId": "rule1",
                "source": "waf",
            },
            "count": 50,
        }
    ]
    processed_firewall = _process_metrics_data(
        raw_data_firewall, "firewallEventsAdaptiveGroups", True
    )
    for item in processed_firewall:
        assert "count" in item
        assert item["count"] == TEST_FIREWALL_EVENT_COUNT  # type: ignore[typeddict-item]


def test_get_datasets_eu(mock_config: CloudflareConfig) -> None:
    """Test dataset selection for EU region."""
    mock_config.cmb_region = CmbRegion.EU
    datasets = _get_datasets(mock_config)
    assert "httpRequestsOverviewAdaptiveGroups" in datasets
    assert "firewallEventsAdaptiveGroups" in datasets
    assert "dnsAnalyticsAdaptiveGroups" not in datasets


def test_get_datasets_global(mock_config: CloudflareConfig) -> None:
    """Test dataset selection for global region."""
    mock_config.cmb_region = CmbRegion.GLOBAL
    datasets = _get_datasets(mock_config)
    assert "httpRequestsOverviewAdaptiveGroups" in datasets
    assert "firewallEventsAdaptiveGroups" in datasets
    assert "dnsAnalyticsAdaptiveGroups" in datasets


def test_get_datasets_with_exclusion(mock_config: CloudflareConfig) -> None:
    """Test dataset selection with exclusions."""
    mock_config.cmb_region = CmbRegion.GLOBAL
    mock_config.exclude_datasets = "firewallEventsAdaptiveGroups"
    datasets = _get_datasets(mock_config)
    assert "firewallEventsAdaptiveGroups" not in datasets
    assert "httpRequestsOverviewAdaptiveGroups" in datasets


TEST_TIMESTAMP = 1234567890.0


def test_buffer_metrics_http() -> None:
    """Test buffering HTTP metrics."""
    processed: list[HttpRequestEntry | FirewallEventEntry] = [
        {
            "dimensions": {"clientCountryName": "US", "edgeResponseStatus": 200},
            "sum": {
                "requests": 100,
                "bytes": 1024,
                "cachedRequests": 0,
                "cachedBytes": 0,
            },
        }
    ]
    http_buf: list[dict[str, object]] = []
    fw_buf: list[dict[str, object]] = []
    _buffer_metrics(processed, "example.com", TEST_TIMESTAMP, http_buf, fw_buf)
    assert len(http_buf) == 1
    assert len(fw_buf) == 0
    assert http_buf[0]["zone"] == "example.com"
    assert http_buf[0]["timestamp"] == TEST_TIMESTAMP


def test_buffer_metrics_firewall() -> None:
    """Test buffering firewall metrics."""
    processed: list[HttpRequestEntry | FirewallEventEntry] = [
        {
            "dimensions": {"action": "block", "ruleId": "r1", "source": "waf"},
            "count": 50,
        }
    ]
    http_buf: list[dict[str, object]] = []
    fw_buf: list[dict[str, object]] = []
    _buffer_metrics(processed, "example.com", TEST_TIMESTAMP, http_buf, fw_buf)
    assert len(http_buf) == 0
    assert len(fw_buf) == 1
    assert fw_buf[0]["zone"] == "example.com"


def test_swap_metrics() -> None:
    """Test atomic metrics swap."""
    collector = CloudflareCollector()
    collector.http_metrics_data = [{"old": "data"}]  # type: ignore[list-item]
    collector.firewall_metrics_data = [{"old": "fw"}]  # type: ignore[list-item]

    new_http = [{"new": "http"}]
    new_fw = [{"new": "fw"}]
    collector.swap_metrics(new_http, new_fw)

    assert collector.http_metrics_data == [{"new": "http"}]
    assert collector.firewall_metrics_data == [{"new": "fw"}]


def test_swap_metrics_empty_clears() -> None:
    """Test that empty swap clears metrics."""
    collector = CloudflareCollector()
    collector.http_metrics_data = [{"old": "data"}]  # type: ignore[list-item]
    collector.firewall_metrics_data = [{"old": "fw"}]  # type: ignore[list-item]

    collector.swap_metrics([], [])

    assert collector.http_metrics_data == []
    assert collector.firewall_metrics_data == []
