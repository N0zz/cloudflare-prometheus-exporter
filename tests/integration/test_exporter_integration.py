"""Integration tests — require a valid CF_API_TOKEN (via .env or environment).

Run locally:  just integration-test
Run in CI:    triggered on pushes to main only (uses GitHub secret)
"""

import contextlib
from collections.abc import Generator

import pytest
from prometheus_client import REGISTRY

from cloudflare_exporter.cloudflare_exporter import cloudflare_fetch_metrics
from cloudflare_exporter.cloudflare_setup import (
    cloudflare_setup_client,
    cloudflare_verify_credentials,
)
from cloudflare_exporter.config import setup_config
from cloudflare_exporter.metrics import COLLECTOR


@pytest.fixture(autouse=True)
def register_collector() -> Generator[None]:
    """Register and clean up the Prometheus collector."""
    with contextlib.suppress(ValueError):
        REGISTRY.register(COLLECTOR)  # type: ignore[arg-type]
    yield
    COLLECTOR.http_metrics_data = []
    COLLECTOR.firewall_metrics_data = []


def test_setup_client_and_verify() -> None:
    """Test that we can authenticate and verify credentials against Cloudflare."""
    client, account = cloudflare_setup_client()

    assert client is not None
    assert account is not None
    assert account.name is not None
    assert account.id is not None

    # Verify credentials are valid
    cloudflare_verify_credentials(client, account)


def test_fetch_metrics_produces_output() -> None:
    """Test that a real metrics fetch populates the collector."""
    client, account = cloudflare_setup_client()
    config = setup_config()

    from cloudflare_exporter.cloudflare_exporter import cloudflare_define_zones

    zones = cloudflare_define_zones(client, config)
    assert len(zones) > 0, "Expected at least one zone"

    # Fetch metrics from Cloudflare
    cloudflare_fetch_metrics(account, client, config, zones)

    # Collector should have data (metrics or at minimum no errors)
    metrics = list(COLLECTOR.collect())
    metric_names = {m.name for m in metrics}

    # These metric families should always be present after a fetch
    assert "cloudflare_requests_total" in metric_names
    assert "cloudflare_scrape_errors_total" in metric_names
    assert "cloudflare_firewall_events_total" in metric_names
