from enum import Enum

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class CmbRegion(str, Enum):
    """Valid Cloudflare Metadata Boundary regions."""

    GLOBAL = "global"
    EU = "eu"
    US = "us"


class CloudflareConfig(BaseSettings):
    """Configuration settings for Cloudflare Exporter.

    All settings can be configured via environment variables with CF_ prefix.
    Example: CF_LISTEN_PORT=8080
    """

    model_config = SettingsConfigDict(env_prefix="CF_", case_sensitive=False)

    # Generic configs
    listen_port: int = Field(
        default=8080,
        ge=1024,
        le=65535,
        description="Port to expose Prometheus metrics on",
    )

    log_level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level",
    )

    max_workers: int = Field(
        default=5,
        ge=3,
        le=10,
        description="Maximum number of concurrent worker threads",
    )

    # Cloudflare configs
    api_token: str = Field(default="", min_length=1, description="Cloudflare API token")

    api_url: str = Field(
        default="https://api.cloudflare.com/client/v4/graphql",
        description="Cloudflare GraphQL API endpoint",
    )

    cmb_region: CmbRegion = Field(
        default=CmbRegion.GLOBAL, description="Cloudflare Metadata Boundary region"
    )

    exclude_datasets: str | None = Field(
        default=None, description="Comma-separated list of datasets to exclude"
    )

    exclude_zones: str | None = Field(
        default=None, description="Comma-separated list of zone IDs to exclude"
    )

    scrape_delay: int = Field(
        default=60, ge=60, le=300, description="Scrape interval in seconds (60-300)"
    )

    zones: str | None = Field(
        default=None, description="Comma-separated list of zone IDs to monitor"
    )

    @field_validator("scrape_delay")
    def validate_scrape_delay(cls, v: int) -> int:  # noqa: N805
        """Validate that scrape_delay is a multiple of 60."""
        if v % 60 != 0:
            raise ValueError("scrape_delay must be a multiple of 60")
        return v


def setup_config() -> CloudflareConfig:
    """Create and validate configuration from environment variables.

    Returns:
        CloudflareConfig: Validated configuration object

    Raises:
        RuntimeError: If configuration validation fails, including missing CF_API_TOKEN
    """
    try:
        return CloudflareConfig()  # Use _env_file to load from environment
    except Exception as e:
        raise RuntimeError(f"Configuration error: {e!s}") from e
