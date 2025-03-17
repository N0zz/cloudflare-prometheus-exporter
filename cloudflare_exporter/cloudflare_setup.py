from typing import Any

from cloudflare import Cloudflare
from dotenv import load_dotenv

from .config import setup_config
from .logger import setup_logger

load_dotenv()

config = setup_config()
logger = setup_logger(config.log_level)


def cloudflare_setup_client() -> tuple[Cloudflare, Any]:
    """Initialize and verify Cloudflare API client.

    Returns:
        Tuple[Cloudflare, Any]: Tuple of (cloudflare client, account info)

    Raises:
        ValueError: If API token is not set
        RuntimeError: If client setup or verification fails
    """
    api_token = config.api_token

    if not api_token:
        raise ValueError("CF_API_TOKEN environment variable is not set")

    try:
        client = Cloudflare(api_token=api_token)
    except Exception as e:
        logger.error("Failed to initialize Cloudflare client", extra={"error": str(e)})
        raise RuntimeError(f"Error setting up Cloudflare client: {e}") from e

    try:
        account = cloudflare_get_account(client)
        cloudflare_verify_credentials(client, account)
        return client, account
    except Exception as e:
        logger.error("Failed to setup Cloudflare client", extra={"error": str(e)})
        raise


def cloudflare_get_account(client: Cloudflare) -> Any:
    """Get first available Cloudflare account.

    Args:
        client: Initialized Cloudflare client

    Returns:
        Any: Account information object

    Raises:
        RuntimeError: If unable to fetch account information
    """
    try:
        accounts_list = client.accounts.list()
        if not accounts_list.result:
            raise RuntimeError("No Cloudflare accounts found")

        account = accounts_list.result[0]
        logger.debug(
            "Successfully retrieved Cloudflare account",
            extra={"account_name": account.name},
        )
        return account

    except Exception as e:
        logger.error("Failed to get Cloudflare account", extra={"error": str(e)})
        raise RuntimeError(f"Could not get Cloudflare account: {e}") from e


def cloudflare_verify_credentials(client: Cloudflare, account: Any) -> None:
    """Verify API token has required permissions.

    Args:
        client: Initialized Cloudflare client
        account: Account information object

    Raises:
        RuntimeError: If token verification fails
    """
    try:
        client.accounts.tokens.verify(account_id=account.id)
        logger.debug("Successfully verified Cloudflare credentials")
    except Exception as e:
        logger.error("Failed to verify Cloudflare credentials", extra={"error": str(e)})
        raise RuntimeError(f"Could not verify Cloudflare token: {e}") from e
