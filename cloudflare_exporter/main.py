import os
import sys
import time
from concurrent.futures import Future, ThreadPoolExecutor
from typing import NoReturn

from cloudflare import Cloudflare
from dotenv import load_dotenv
from prometheus_client import start_http_server

# Add the parent directory to the Python path if running as a script
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cloudflare_exporter.cloudflare_exporter import (
    cloudflare_define_zones,
    cloudflare_fetch_metrics,
)
from cloudflare_exporter.cloudflare_setup import cloudflare_setup_client
from cloudflare_exporter.config import CloudflareConfig, setup_config
from cloudflare_exporter.logger import setup_logger

# Load environment variables
load_dotenv()

# Initialize config and logger at module level
config = setup_config()
logger = setup_logger(config.log_level)


def setup_environment() -> tuple[Cloudflare, list[str], CloudflareConfig, Cloudflare]:
    """Initialize application environment.

    Returns:
        tuple[Cloudflare, list[str], CloudflareConfig, Cloudflare]:
        Tuple of (cloudflare client, zones list, config, account)

    Raises:
        RuntimeError: If initialization fails
    """
    logger.info("Starting Cloudflare exporter...")

    try:
        client, account = cloudflare_setup_client()
        logger.info(f"Successfully connected to account: {account.name}")

        zones = cloudflare_define_zones(client, config)
        if not zones:
            raise RuntimeError("No zones found to monitor")
        logger.info(f"Found {len(zones)} zones to monitor")

        return client, zones, config, account
    except Exception as e:
        logger.error("Failed to initialize environment", extra={"error": str(e)})
        raise


def start_metrics_server(port: int) -> None:
    """Start Prometheus metrics HTTP server.

    Args:
        port: Port number to listen on

    Raises:
        RuntimeError: If server fails to start
    """
    try:
        start_http_server(port)
        logger.info(f"Prometheus metrics server started on port {port}")
    except Exception as e:
        logger.error("Failed to start metrics server", extra={"error": str(e)})
        raise RuntimeError(f"Could not start metrics server: {e}") from e


def metrics_collection_loop(
    executor: ThreadPoolExecutor,
    account: Cloudflare,
    client: Cloudflare,
    config: CloudflareConfig,
    zones: list[str],
) -> NoReturn:
    """Main metrics collection loop.

    Args:
        executor: ThreadPoolExecutor instance
        client: Cloudflare API client
        config: Application configuration
        zones: List of zone IDs to monitor

    Note:
        This function runs indefinitely until interrupted
    """
    current_task: Future[None] | None = None

    while True:
        try:
            # Wait for previous task to complete if it exists
            if current_task:
                try:
                    current_task.result(timeout=0)
                except Exception as e:
                    logger.error(
                        "Error in previous metrics collection", extra={"error": str(e)}
                    )

            # Submit new task
            current_task = executor.submit(
                cloudflare_fetch_metrics, account, client, config, zones
            )

            # Sleep for the configured interval
            time.sleep(config.scrape_delay)

        except Exception as e:
            logger.error("Error in metrics collection loop", extra={"error": str(e)})
            time.sleep(1)  # Brief pause on error


def main() -> None:
    """Main application entry point."""
    try:
        # Initialize environment
        client, zones, config, account = setup_environment()

        # Start metrics server
        start_metrics_server(config.listen_port)

        # Start metrics collection
        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            metrics_collection_loop(executor, account, client, config, zones)

    except Exception as e:
        logger.error("Fatal error in main application", extra={"error": str(e)})
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        sys.exit(0)
