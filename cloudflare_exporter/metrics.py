import threading
from collections.abc import Generator
from datetime import datetime
from typing import NotRequired, TypedDict

from dotenv import load_dotenv
from prometheus_client import REGISTRY
from prometheus_client.core import GaugeMetricFamily

from .config import setup_config
from .logger import setup_logger

load_dotenv()

config = setup_config()
logger = setup_logger(config.log_level)


class HttpRequestDimensions(TypedDict):
    """Dimensions specific to HTTP request metrics"""

    edgeResponseStatus: int
    clientCountryName: str


class FirewallEventDimensions(TypedDict):
    """Dimensions specific to firewall event metrics"""

    action: str
    ruleId: str
    source: str


class HttpRequestMetrics(TypedDict):
    """Metrics specific to HTTP requests"""

    requests: int
    bytes: int
    cachedRequests: int
    cachedBytes: int


class FirewallEventMetrics(TypedDict):
    """Metrics specific to firewall events"""

    count: int


class HttpRequestEntry(TypedDict):
    """Entry type for HTTP request metrics"""

    dimensions: HttpRequestDimensions
    sum: HttpRequestMetrics
    zone: NotRequired[str]
    timestamp: NotRequired[float]


class FirewallEventEntry(TypedDict):
    """Entry type for firewall event metrics"""

    dimensions: FirewallEventDimensions
    count: int
    zone: NotRequired[str]
    timestamp: NotRequired[float]


# Use Union type to handle different metric types
MetricEntry = HttpRequestEntry | FirewallEventEntry


class CloudflareCollector:
    """Prometheus collector for Cloudflare metrics.

    This collector maintains thread-safe storage of Cloudflare metrics and implements
    the Prometheus collector interface to expose these metrics in the required format.

    Attributes:
        http_metrics_data (List[Dict]): Thread-safe storage for HTTP metrics
        firewall_metrics_data (List[Dict]): Thread-safe storage for firewall metrics
        _lock (threading.Lock): Lock for thread-safe access to metrics_data
        scrape_errors (int): Counter for scrape errors
        account_name (str): Name of the Cloudflare account
        account_id (str): ID of the Cloudflare account
        max_quota (int): Maximum enterprise zone quota
        current_quota (int): Current enterprise zone quota usage
        available_quota (int): Available enterprise zone quota
    """

    def __init__(self) -> None:
        """Initialize the collector with empty metrics and a thread lock."""
        self.http_metrics_data: list[HttpRequestEntry] = []
        self.firewall_metrics_data: list[FirewallEventEntry] = (
            []
        )  # Separate list for firewall metrics
        self._lock = threading.Lock()
        self.scrape_errors: int = 0
        self.account_name: str | None = None
        self.account_id: str | None = None

        self.enterprise_quota_max = GaugeMetricFamily(
            "cloudflare_enterprise_zone_quota_max",
            "Maximum enterprise zone quota",
            labels=["account", "account_id"],
        )
        self.enterprise_quota_current = GaugeMetricFamily(
            "cloudflare_enterprise_zone_quota_current",
            "Current enterprise zone quota usage",
            labels=["account", "account_id"],
        )
        self.enterprise_quota_available = GaugeMetricFamily(
            "cloudflare_enterprise_zone_quota_available",
            "Available enterprise zone quota",
            labels=["account", "account_id"],
        )
        # New attributes to store quota values
        self.max_quota: float = 0.0
        self.current_quota: float = 0.0
        self.available_quota: float = 0.0

    def _update_metrics(
        self,
        data: list[MetricEntry] | None,
        zone_name: str | None,
        timestamp: str,
        account_name: str,
        account_id: str,
        max_quota: float | None,
        current_quota: float | None,
        available_quota: float | None,
    ) -> None:
        """Update the stored metrics with new data.

        Args:
            data: List of metric entries from API, or None if only updating quotas
            zone_name: Name of the Cloudflare zone, or None if only updating quotas
            timestamp: ISO formatted timestamp for the metrics
            account_name: Name of the Cloudflare account
            account_id: ID of the Cloudflare account
            max_quota: Maximum enterprise quota, or None if not updating quotas
            current_quota: Current enterprise quota, or None if not updating quotas
            available_quota: Available enterprise quota, or None if not updating quotas
        """
        self.account_name = account_name
        self.account_id = account_id

        metric_timestamp = datetime.strptime(
            timestamp, "%Y-%m-%dT%H:%M:%SZ"
        ).timestamp()

        # Store the timestamp for quota metrics
        self.quota_timestamp = metric_timestamp

        # Update metrics data if provided
        if data and zone_name:
            new_http_metrics: list[MetricEntry] = []
            new_firewall_metrics: list[MetricEntry] = []
            for entry in data:
                # Determine the type of metric and create the new_metric accordingly
                if "sum" in entry:
                    new_http_metric: HttpRequestEntry = {
                        "dimensions": entry["dimensions"],  # type: ignore[typeddict-item]
                        "sum": entry["sum"],  # type: ignore[typeddict-item]
                        "zone": zone_name,
                        "timestamp": metric_timestamp,
                    }
                    new_http_metrics.append(new_http_metric)
                elif "count" in entry:
                    new_firewall_metric: FirewallEventEntry = {
                        "dimensions": entry["dimensions"],
                        "count": entry["count"],
                        "zone": zone_name,
                        "timestamp": metric_timestamp,
                    }
                    new_firewall_metrics.append(new_firewall_metric)

            with self._lock:
                # Append new metrics instead of replacing
                if new_http_metrics and isinstance(new_http_metrics[0]["sum"], dict):  # type: ignore[typeddict-item]
                    self.http_metrics_data.extend(
                        [m for m in new_http_metrics if "sum" in m]  # type: ignore[misc]
                    )
                elif new_firewall_metrics and isinstance(
                    new_firewall_metrics[0]["count"], int  # type: ignore[typeddict-item]
                ):
                    self.firewall_metrics_data.extend(
                        [m for m in new_firewall_metrics if "count" in m]  # type: ignore[misc]
                    )
                logger.debug(f"Incoming data: {data}")
        elif zone_name:
            logger.info(f"No new data to update for zone: {zone_name}")

        # Update quota metrics if provided
        if all(
            quota is not None for quota in (max_quota, current_quota, available_quota)
        ):
            with self._lock:
                # Runtime type checks instead of assertions
                if any(
                    quota is None
                    for quota in (max_quota, current_quota, available_quota)
                ):
                    raise ValueError("Quota values cannot be None at this point")

                # TypeScript narrowing - now the type checker knows these aren't None
                self.max_quota = max_quota  # type: ignore[assignment]
                self.current_quota = current_quota  # type: ignore[assignment]
                self.available_quota = available_quota  # type: ignore[assignment]
                logger.debug("Updated quota metrics")

    def collect(self) -> Generator[GaugeMetricFamily]:
        """Collect and yield Prometheus metrics.

        This method implements the collector interface required by Prometheus.
        It creates four gauge metrics:
        - cloudflare_requests_total: Total number of HTTP requests
        - cloudflare_bytes_total: Total bytes transferred
        - cloudflare_cached_requests_total: Total number of cached HTTP requests
        - cloudflare_cached_bytes_total: Total cached bytes transferred

        Returns:
            Generator[GaugeMetricFamily, None, None]:
            Generator yielding Prometheus gauge metrics

        Note:
            Each metric includes labels for:
            - zone: Cloudflare zone name
            - country: Client country name
            - status: Edge response status
        """
        with self._lock:
            http_metrics_snapshot = list(self.http_metrics_data)
            firewall_metrics_snapshot = list(self.firewall_metrics_data)

        # Reset quota metrics
        self.enterprise_quota_max.samples.clear()
        self.enterprise_quota_current.samples.clear()
        self.enterprise_quota_available.samples.clear()

        # HTTP request metrics
        requests = GaugeMetricFamily(
            "cloudflare_requests_total",
            "Total number of HTTP requests",
            labels=["zone", "country", "status", "account", "account_id"],
        )
        bytes_total = GaugeMetricFamily(
            "cloudflare_bytes_total",
            "Total bytes transferred",
            labels=["zone", "country", "status", "account", "account_id"],
        )
        cached_requests = GaugeMetricFamily(
            "cloudflare_cached_requests_total",
            "Total number of cached HTTP requests",
            labels=["zone", "country", "status", "account", "account_id"],
        )
        cached_bytes = GaugeMetricFamily(
            "cloudflare_cached_bytes_total",
            "Total cached bytes transferred",
            labels=["zone", "country", "status", "account", "account_id"],
        )

        # Firewall metrics
        firewall_events = GaugeMetricFamily(
            "cloudflare_firewall_events_total",
            "Total number of firewall events",
            labels=[
                "zone",
                "action",
                "rule_id",
                "source",
                "account",
                "account_id",
            ],
        )

        errors = GaugeMetricFamily(
            "cloudflare_scrape_errors_total",
            "Total number of scrape errors",
            labels=["account", "account_id"],
        )

        # Process HTTP metrics
        for item in http_metrics_snapshot:
            if "sum" in item:
                labels = [
                    str(item.get("zone", "")),
                    str(item["dimensions"]["clientCountryName"]),
                    str(item["dimensions"]["edgeResponseStatus"]),
                    str(self.account_name or ""),
                    str(self.account_id or ""),
                ]
                timestamp = item.get("timestamp")
                sum_data = item["sum"]

                requests.add_metric(labels, float(sum_data["requests"]), timestamp)
                bytes_total.add_metric(labels, float(sum_data["bytes"]), timestamp)
                cached_requests.add_metric(
                    labels, float(sum_data["cachedRequests"]), timestamp
                )
                cached_bytes.add_metric(
                    labels, float(sum_data["cachedBytes"]), timestamp
                )

        # Process firewall metrics
        for item in firewall_metrics_snapshot:  # type: ignore[assignment]
            if "count" in item:
                labels = [
                    str(item.get("zone", "")),
                    str(item["dimensions"]["action"]),  # type: ignore[typeddict-item]
                    str(item["dimensions"]["ruleId"]),  # type: ignore[typeddict-item]
                    str(item["dimensions"]["source"]),  # type: ignore[typeddict-item]
                    str(self.account_name or ""),
                    str(self.account_id or ""),
                ]
                timestamp = item.get("timestamp")
                firewall_events.add_metric(labels, float(item["count"]), timestamp)  # type: ignore[typeddict-item]

        # Yield new enterprise zone quota metrics
        if (
            self.account_name and self.account_id
        ):  # Check if account name and ID are set
            self.enterprise_quota_max.add_metric(
                [self.account_name, self.account_id],
                self.max_quota,
                timestamp=self.quota_timestamp,
            )
            self.enterprise_quota_current.add_metric(
                [self.account_name, self.account_id],
                self.current_quota,
                timestamp=self.quota_timestamp,
            )
            self.enterprise_quota_available.add_metric(
                [self.account_name, self.account_id],
                self.available_quota,
                timestamp=self.quota_timestamp,
            )

        errors.add_metric(
            [str(self.account_name or ""), str(self.account_id or "")],
            self.scrape_errors,
        )

        yield requests
        yield bytes_total
        yield cached_requests
        yield cached_bytes
        yield firewall_events
        yield errors
        yield self.enterprise_quota_max
        yield self.enterprise_quota_current
        yield self.enterprise_quota_available

    def increment_error_counter(self) -> None:
        """Increment the scrape error counter."""
        with self._lock:
            self.scrape_errors += 1

    def cleanup_old_metrics(
        self,
        # We keep metrics for 2x scrape delay to avoid gaps in the metrics
        max_age_seconds: int = config.scrape_delay * 2,
    ) -> None:
        """Remove metrics older than max_age_seconds."""
        current_time = datetime.now().timestamp()

        logger.debug(f"Cleaning up old metrics, max_age_seconds: {max_age_seconds}")

        with self._lock:
            self.http_metrics_data = [
                m
                for m in self.http_metrics_data
                if current_time - m.get("timestamp", 0) <= max_age_seconds
            ]
            self.firewall_metrics_data = [
                m
                for m in self.firewall_metrics_data
                if current_time - m.get("timestamp", 0) <= max_age_seconds
            ]


# Create a global collector instance
COLLECTOR = CloudflareCollector()
REGISTRY.register(COLLECTOR)  # type: ignore[arg-type]


def prometheus_generate_metrics(
    data: list[MetricEntry] | None,
    zone_name: str | None,
    timestamp: str,
    max_quota: float | None,
    current_quota: float | None,
    available_quota: float | None,
    account_name: str,
    account_id: str,
) -> None:
    """Update Prometheus metrics with new Cloudflare data.

    This function serves as the main entry point for updating metrics. It delegates
    the actual update to the global collector instance.

    Args:
        data: List of metric entries from Cloudflare API
        zone_name: Name of the Cloudflare zone
        timestamp: ISO formatted timestamp for the metrics
        max_quota: Maximum enterprise zone quota
        current_quota: Current enterprise zone quota usage
        available_quota: Available enterprise zone quota
        account_name: Name of the Cloudflare account
        account_id: ID of the Cloudflare account

    Note:
        This function is thread-safe as it uses the collector's thread-safe
        update mechanism.
    """
    COLLECTOR._update_metrics(
        data,
        zone_name,
        timestamp,
        account_name,
        account_id,
        max_quota,
        current_quota,
        available_quota,
    )
