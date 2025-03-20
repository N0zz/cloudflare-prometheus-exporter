import os
import sys
from unittest.mock import MagicMock

import pytest

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def mock_cloudflare_client() -> MagicMock:
    """Fixture providing a mock Cloudflare client."""
    client = MagicMock()
    return client


@pytest.fixture
def test_env() -> None:  # type: ignore[misc]
    """Fixture providing test environment variables."""
    os.environ["CF_API_TOKEN"] = "test_token"
    os.environ["CF_CMB_REGION"] = "global"
    os.environ["CF_SCRAPE_DELAY"] = "60"
    yield
    # Clean up environment after tests
    for key in ["CF_API_TOKEN", "CF_CMB_REGION", "CF_SCRAPE_DELAY"]:
        os.environ.pop(key, None)
