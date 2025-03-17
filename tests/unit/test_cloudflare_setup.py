import os
from unittest.mock import MagicMock, patch

import pytest
from cloudflare import Cloudflare

from cloudflare_exporter.cloudflare_setup import (
    cloudflare_get_account,
    cloudflare_setup_client,
    cloudflare_verify_credentials,
)


@pytest.fixture
def mock_cloudflare() -> tuple[MagicMock, MagicMock]:
    """Fixture providing a mock Cloudflare client."""
    mock_client = MagicMock(spec=Cloudflare)
    mock_account = MagicMock()
    mock_account.id = "test_account_id"
    mock_account.name = "test_account"

    mock_accounts_list = MagicMock()
    mock_accounts_list.result = [mock_account]
    mock_client.accounts.list.return_value = mock_accounts_list

    return mock_client, mock_account


@pytest.fixture(autouse=True)
def clean_env() -> None:  # type: ignore[misc]
    """Clean environment variables before each test."""
    old_env = dict(os.environ)
    for key in list(os.environ.keys()):
        if key.startswith("CF_"):
            del os.environ[key]
    yield
    os.environ.clear()
    os.environ.update(old_env)


def test_cloudflare_setup_client_success(
    mock_cloudflare: tuple[MagicMock, MagicMock], test_env: None
) -> None:
    """Test successful client setup."""
    mock_client, mock_account = mock_cloudflare

    with patch(
        "cloudflare_exporter.cloudflare_setup.Cloudflare", return_value=mock_client
    ):
        client, account = cloudflare_setup_client()

        assert client == mock_client
        assert account == mock_account
        mock_client.accounts.list.assert_called_once()
        mock_client.accounts.tokens.verify.assert_called_once_with(
            account_id=mock_account.id
        )


def test_cloudflare_setup_client_no_token(clean_env: None) -> None:
    """Test client setup with missing API token."""
    # Ensure clean environment
    if "CF_API_TOKEN" in os.environ:
        del os.environ["CF_API_TOKEN"]

    # Mock config to ensure it doesn't use real environment
    with patch("cloudflare_exporter.cloudflare_setup.config") as mock_config:
        mock_config.api_token = ""
        with pytest.raises(ValueError) as exc_info:
            cloudflare_setup_client()
        assert "CF_API_TOKEN environment variable is not set" in str(exc_info.value)


def test_cloudflare_setup_client_init_failure(test_env: None) -> None:
    """Test client setup with initialization failure."""
    with patch(
        "cloudflare_exporter.cloudflare_setup.Cloudflare",
        side_effect=Exception("API Error"),
    ):
        with pytest.raises(RuntimeError) as exc_info:
            cloudflare_setup_client()
        assert "Error setting up Cloudflare client" in str(exc_info.value)


def test_cloudflare_get_account_success(
    mock_cloudflare: tuple[MagicMock, MagicMock],
) -> None:
    """Test successful account retrieval."""
    mock_client, mock_account = mock_cloudflare

    result = cloudflare_get_account(mock_client)
    assert result == mock_account
    mock_client.accounts.list.assert_called_once()


def test_cloudflare_get_account_no_accounts(
    mock_cloudflare: tuple[MagicMock, MagicMock],
) -> None:
    """Test account retrieval with no accounts."""
    mock_client, _ = mock_cloudflare
    mock_client.accounts.list.return_value.result = []

    with pytest.raises(RuntimeError) as exc_info:
        cloudflare_get_account(mock_client)
    assert "No Cloudflare accounts found" in str(exc_info.value)


def test_cloudflare_get_account_api_error(
    mock_cloudflare: tuple[MagicMock, MagicMock],
) -> None:
    """Test account retrieval with API error."""
    mock_client, _ = mock_cloudflare
    mock_client.accounts.list.side_effect = Exception("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        cloudflare_get_account(mock_client)
    assert "Could not get Cloudflare account" in str(exc_info.value)


def test_cloudflare_verify_credentials_success(
    mock_cloudflare: tuple[MagicMock, MagicMock],
) -> None:
    """Test successful credentials verification."""
    mock_client, mock_account = mock_cloudflare

    cloudflare_verify_credentials(mock_client, mock_account)
    mock_client.accounts.tokens.verify.assert_called_once_with(
        account_id=mock_account.id
    )


def test_cloudflare_verify_credentials_failure(
    mock_cloudflare: tuple[MagicMock, MagicMock],
) -> None:
    """Test credentials verification failure."""
    mock_client, mock_account = mock_cloudflare
    mock_client.accounts.tokens.verify.side_effect = Exception("Invalid token")

    with pytest.raises(RuntimeError) as exc_info:
        cloudflare_verify_credentials(mock_client, mock_account)
    assert "Could not verify Cloudflare token" in str(exc_info.value)
