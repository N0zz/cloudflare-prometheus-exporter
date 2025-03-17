import os
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import ANY, MagicMock, patch

import pytest

from cloudflare_exporter.config import CloudflareConfig
from cloudflare_exporter.main import (
    main,
    metrics_collection_loop,
    setup_environment,
    start_metrics_server,
)


@pytest.fixture
def mock_environment(
    mocker: MagicMock,
) -> tuple[MagicMock, list[str], CloudflareConfig]:
    """Set up mock environment for testing."""
    from cloudflare_exporter.config import CmbRegion

    client = mocker.MagicMock()
    zones = ["023e105f4ecef8ad9ca31a8372d0c353", "023e105f4ecef8ad9ca31a8372d0c354"]
    config = CloudflareConfig(
        api_token="test-token",
        max_workers=5,
        listen_port=8080,
        scrape_delay=60,
        cmb_region=CmbRegion.EU,
    )

    return client, zones, config


@pytest.fixture
def test_env(mocker: MagicMock) -> None:
    """Mock environment variables for testing."""
    env_vars = {
        "CF_API_TOKEN": "test-token",
        "CF_API_URL": "https://api.cloudflare.com/client/v4/graphql",
        "CF_ZONES": None,
        "CF_EXCLUDE_ZONES": None,
        "CF_CMB_REGION": "eu",
        "SCRAPE_INTERVAL": "300",
        "SCRAPE_TIMEOUT": "30",
        "SCRAPE_DELAY": "60",
        "LOG_LEVEL": "INFO",
    }
    for key, value in env_vars.items():
        mocker.patch.dict(
            os.environ, {key: value} if value is not None else {}, clear=True
        )


def test_setup_environment_success(
    mock_environment: tuple[MagicMock, list[str], CloudflareConfig], test_env: None
) -> None:
    """Test successful environment setup."""
    client, zones, config = mock_environment

    with (
        patch(
            "cloudflare_exporter.main.cloudflare_setup_client",
            return_value=(client, MagicMock()),
        ),
        patch("cloudflare_exporter.main.cloudflare_define_zones", return_value=zones),
        patch("cloudflare_exporter.main.setup_config", return_value=config),
        patch("cloudflare_exporter.main.config", config),
    ):
        result_client, result_zones, result_config, result_account = setup_environment()
        assert result_client == client
        assert result_zones == zones
        assert result_config.model_dump() == config.model_dump()
        assert isinstance(result_account, MagicMock)


def test_setup_environment_no_zones(
    mock_environment: tuple[MagicMock, list[str], CloudflareConfig], test_env: None
) -> None:
    """Test environment setup with no zones."""
    client, _, config = mock_environment

    with (
        patch(
            "cloudflare_exporter.main.cloudflare_setup_client",
            return_value=(client, MagicMock()),
        ),
        patch("cloudflare_exporter.main.cloudflare_define_zones", return_value=[]),
        patch("cloudflare_exporter.main.setup_config", return_value=config),
    ):

        with pytest.raises(RuntimeError) as exc_info:
            setup_environment()
        assert "No zones found to monitor" in str(exc_info.value)


def test_start_metrics_server_success() -> None:
    """Test successful metrics server start."""
    with patch("cloudflare_exporter.main.start_http_server") as mock_start:
        start_metrics_server(8080)
        mock_start.assert_called_once_with(8080)


def test_start_metrics_server_failure() -> None:
    """Test metrics server start failure."""
    with patch(
        "cloudflare_exporter.main.start_http_server",
        side_effect=Exception("Server error"),
    ):
        with pytest.raises(RuntimeError) as exc_info:
            start_metrics_server(8080)
        assert "Could not start metrics server" in str(exc_info.value)


def test_metrics_collection_loop(
    mock_environment: tuple[MagicMock, list[str], CloudflareConfig],
) -> None:
    """Test metrics collection loop."""
    client, zones, config = mock_environment
    config.max_workers = 1  # Set concrete value for ThreadPoolExecutor
    mock_account = MagicMock()

    with (
        patch("cloudflare_exporter.main.cloudflare_fetch_metrics") as mock_fetch,
        patch("cloudflare_exporter.main.time.sleep", side_effect=KeyboardInterrupt),
    ):  # Interrupt immediately
        with ThreadPoolExecutor(max_workers=1) as executor:
            try:
                metrics_collection_loop(executor, mock_account, client, config, zones)
            except KeyboardInterrupt:
                pass

        mock_fetch.assert_called_once_with(mock_account, client, config, zones)


def test_metrics_collection_loop_error_handling(
    mock_environment: tuple[MagicMock, list[str], CloudflareConfig],
) -> None:
    """Test error handling in metrics collection loop."""
    client, zones, config = mock_environment
    mock_account = MagicMock()

    # Mock fetch_metrics to raise an exception
    with (
        patch(
            "cloudflare_exporter.main.cloudflare_fetch_metrics",
            side_effect=Exception("Fetch error"),
        ),
        patch(
            "cloudflare_exporter.main.time.sleep", side_effect=[None, KeyboardInterrupt]
        ),
    ):  # Run once then interrupt

        with ThreadPoolExecutor(max_workers=1) as executor:
            try:
                metrics_collection_loop(executor, mock_account, client, config, zones)
            except KeyboardInterrupt:
                pass


@patch("cloudflare_exporter.main.setup_environment")
@patch("cloudflare_exporter.main.start_metrics_server")
@patch("cloudflare_exporter.main.metrics_collection_loop")
def test_main_success(
    mock_loop: MagicMock,
    mock_server: MagicMock,
    mock_setup: MagicMock,
    mock_environment: tuple[MagicMock, list[str], CloudflareConfig],
) -> None:
    """Test successful main function execution."""
    client, zones, config = mock_environment
    mock_account = MagicMock()
    mock_setup.return_value = (client, zones, config, mock_account)

    # Instead of raising KeyboardInterrupt, just return normally
    mock_loop.return_value = None

    main()  # No need for pytest.raises here since we're testing normal execution

    mock_setup.assert_called_once()
    mock_server.assert_called_once_with(config.listen_port)
    mock_loop.assert_called_once_with(ANY, mock_account, client, config, zones)


@patch(
    "cloudflare_exporter.main.setup_environment", side_effect=Exception("Setup error")
)
def test_main_failure(mock_setup: MagicMock) -> None:
    """Test main function failure handling."""
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
