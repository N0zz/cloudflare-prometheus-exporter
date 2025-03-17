import os

import pytest
from pydantic import ValidationError

from cloudflare_exporter.config import CloudflareConfig, CmbRegion, setup_config

# Default configuration values
DEFAULT_PORT = 8080
DEFAULT_MAX_WORKERS = 5
DEFAULT_SCRAPE_DELAY = 60


@pytest.fixture(autouse=True)
def clean_env() -> None:  # type: ignore[misc]
    """Clean environment variables before each test."""
    # Save original env
    old_env = dict(os.environ)
    # Clean CF_ variables
    for key in list(os.environ.keys()):
        if key.startswith("CF_"):
            del os.environ[key]
    # Set minimum required env vars
    os.environ["CF_API_TOKEN"] = "test_token"
    yield
    # Restore original env
    os.environ.clear()
    os.environ.update(old_env)


def test_config_defaults(clean_env: None) -> None:
    """Test default configuration values."""
    config = CloudflareConfig()
    assert config.listen_port == DEFAULT_PORT
    assert config.log_level == "INFO"
    assert config.max_workers == DEFAULT_MAX_WORKERS
    assert config.api_url == "https://api.cloudflare.com/client/v4/graphql"
    assert config.cmb_region == CmbRegion.GLOBAL
    assert config.scrape_delay == DEFAULT_SCRAPE_DELAY
    assert config.exclude_zones is None
    assert config.zones is None


def test_config_validation() -> None:
    """Test configuration validation."""
    with pytest.raises(ValidationError):
        CloudflareConfig(scrape_delay=45)  # Not a multiple of 60

    with pytest.raises(ValidationError):
        CloudflareConfig(listen_port=80)  # Port below 1024

    with pytest.raises(ValidationError):
        CloudflareConfig(max_workers=11)  # Above max workers limit

    with pytest.raises(ValidationError):
        CloudflareConfig(log_level="INVALID")  # Invalid log level


def test_cmb_region_enum() -> None:
    """Test CmbRegion enum values."""
    assert CmbRegion.GLOBAL.value == "global"
    assert CmbRegion.EU.value == "eu"
    assert CmbRegion.US.value == "us"

    # Test invalid region
    with pytest.raises(ValidationError):
        CloudflareConfig(cmb_region="invalid")  # type: ignore[arg-type]


def test_setup_config(test_env: None) -> None:
    """Test setup_config function."""
    config = setup_config()
    assert isinstance(config, CloudflareConfig)
    assert config.api_token == "test_token"


def test_setup_config_failure(clean_env: None) -> None:
    """Test setup_config function with invalid configuration."""
    # Remove required environment variable
    if "CF_API_TOKEN" in os.environ:
        del os.environ["CF_API_TOKEN"]

    with pytest.raises(RuntimeError) as exc_info:
        setup_config()  # Should fail without API token
    assert "Configuration error" in str(exc_info.value)
