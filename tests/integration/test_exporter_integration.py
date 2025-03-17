import threading
import time
from unittest.mock import MagicMock, patch

import pytest
import requests
from cloudflare import Cloudflare
from prometheus_client import REGISTRY

from cloudflare_exporter.main import setup_environment, start_metrics_server
from cloudflare_exporter.metrics import COLLECTOR

# HTTP Status Codes
HTTP_OK = 200


@pytest.fixture(autouse=True)
def setup_collector() -> None:  # type: ignore[misc]
    """Fixture to handle collector setup and cleanup."""
    # Initialize collector with test data
    COLLECTOR.account_name = "test_account"
    COLLECTOR.account_id = "test_account_id"
    COLLECTOR.max_quota = 1000
    COLLECTOR.current_quota = 500
    COLLECTOR.available_quota = 500
    COLLECTOR.quota_timestamp = time.time()

    # Make sure collector is registered
    try:
        REGISTRY.register(COLLECTOR)  # type: ignore[arg-type]
    except ValueError:
        # Collector already registered, that's fine
        pass

    yield

    # Cleanup after test
    try:
        REGISTRY.unregister(COLLECTOR)  # type: ignore[arg-type]
    except KeyError:
        # Collector already unregistered, that's fine
        pass


@pytest.fixture
def mock_cloudflare_response() -> dict[str, object]:
    return {
        "data": {
            "viewer": {
                "zones": [
                    {
                        "httpRequestsOverviewAdaptiveGroups": [
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
                        ],
                        "firewallEventsAdaptiveGroups": [
                            {
                                "dimensions": {
                                    "action": "block",
                                    "ruleId": "rule1",
                                    "source": "waf",
                                },
                                "count": 50,
                            }
                        ],
                    }
                ]
            }
        }
    }


@pytest.fixture
def mock_cloudflare_client(mock_cloudflare_response: dict[str, object]) -> MagicMock:
    client = MagicMock(spec=Cloudflare)
    zone = MagicMock()
    zone.id = "023e105f4ecef8ad9ca31a8372d0c353"
    zone.name = "test-domain.example.com"
    client.zones.list.return_value.result = [zone]
    client.post = MagicMock(return_value=mock_cloudflare_response)
    return client


def test_metrics_endpoint_integration(
    mock_cloudflare_client: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test the complete flow from server startup to metrics collection."""
    port = 8081

    # Mock environment setup
    monkeypatch.setenv("CF_API_TOKEN", "test-token")
    monkeypatch.setenv("CF_API_URL", "https://api.cloudflare.com/client/v4/graphql")
    monkeypatch.setenv("CF_LISTEN_PORT", str(port))
    monkeypatch.setenv("SCRAPE_DELAY", "60")
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    # Set up the environment
    client, zones, config, account_mock = setup_environment()

    # Start the metrics server in a separate thread
    server_thread = threading.Thread(
        target=start_metrics_server, args=(port,), daemon=True
    )
    server_thread.start()

    # Give the server time to start
    time.sleep(2)

    try:
        # Test the metrics endpoint using the configured port
        response = requests.get(f"http://localhost:{port}/metrics")
        assert response.status_code == HTTP_OK
        metrics_text = response.text

        # Verify expected metrics are present
        assert "cloudflare_requests_total" in metrics_text
    finally:
        # Server cleanup is handled by daemon thread
        pass


@patch("cloudflare_exporter.cloudflare_exporter._make_cloudflare_request")
def test_metrics_collection_error_handling(
    mock_request: MagicMock,
    mock_cloudflare_client: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test error handling during metrics collection."""
    port = 8082

    # Mock environment setup
    monkeypatch.setenv("CF_API_TOKEN", "test-token")
    monkeypatch.setenv("CF_API_URL", "https://api.cloudflare.com/client/v4/graphql")
    monkeypatch.setenv("CF_LISTEN_PORT", str(port))

    # Set up the environment
    client, zones, config, account_mock = setup_environment()

    # Simulate an API error
    mock_request.side_effect = requests.exceptions.RequestException("API Error")

    # Start the metrics server
    server_thread = threading.Thread(
        target=start_metrics_server, args=(port,), daemon=True
    )
    server_thread.start()
    time.sleep(2)

    try:
        # The metrics endpoint should still respond even if collection fails
        response = requests.get(f"http://localhost:{port}/metrics")
        assert response.status_code == HTTP_OK
        metrics_text = response.text
        # Should contain error metrics
        assert "cloudflare_scrape_errors_total" in metrics_text
    finally:
        # Server cleanup is handled by daemon thread
        pass
