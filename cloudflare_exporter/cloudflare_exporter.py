import os
import time
from datetime import UTC, datetime, timedelta
from typing import Any

import requests
from dotenv import load_dotenv

from .config import CloudflareConfig, setup_config
from .logger import setup_logger
from .metrics import (
    COLLECTOR,
    FirewallEventEntry,
    HttpRequestEntry,
    prometheus_generate_metrics,
)

load_dotenv()

config = setup_config()
logger = setup_logger(config.log_level)


def _get_query(query_file_path: str) -> str:
    """Read and return GraphQL query from file.

    Args:
        query_file_path: Path to the .gql query file

    Returns:
        str: Contents of the query file
    """
    # Get the directory where this file is located
    package_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(package_dir, query_file_path)

    try:
        with open(full_path) as query_file:
            return query_file.read()
    except FileNotFoundError:
        logger.error(f"Query file not found: {full_path}")
        raise


def _rounddown_time(time: datetime) -> str:
    """Round down datetime to minute precision and format for Cloudflare API.

    Args:
        time: Datetime to round down

    Returns:
        str: ISO formatted time string with 'Z' suffix
    """
    rounded_time = (
        time.replace(second=0, microsecond=0).isoformat().replace("+00:00", "Z")
    )
    return rounded_time


def cloudflare_define_zones(client: Any, config: CloudflareConfig) -> list[str]:
    """Get list of zone IDs to monitor based on configuration.

    Args:
        client: Cloudflare API client
        config: Application configuration dictionary

    Returns:
        List[str]: List of zone IDs to monitor
    """
    cfg_zones = config.zones
    cfg_exclude_zones = config.exclude_zones

    if cfg_zones is not None:
        zones = cfg_zones.split(",")
    else:
        all_zones_data = client.zones.list()
        zones = [
            zone.id for zone in all_zones_data.result
        ]  # List comprehension instead of map

    if cfg_exclude_zones is not None:
        zones = [zone for zone in zones if zone not in cfg_exclude_zones.split(",")]

    return zones


def _make_cloudflare_request(
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    max_retries: int = 3,
    timeout: int = 30,
) -> dict[str, Any]:
    """Make request to Cloudflare API.

    Args:
        url: Cloudflare API endpoint
        headers: Request headers
        payload: Request payload
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds

    Returns:
        Dict[str, Any]: JSON response from API

    Raises:
        Exception: If request fails after all retries
    """
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=timeout
            )
            response.raise_for_status()
            return dict(response.json())  # Cast to dict
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                COLLECTOR.increment_error_counter()
                raise Exception(
                    f"Failed to fetch Cloudflare data after {max_retries} attempts: {e}"
                ) from e
            logger.warning(
                f"Request failed (attempt {attempt + 1}/{max_retries}): {e!s}"
            )
            time.sleep(2**attempt)  # Exponential backoff
    return {}  # Add explicit return for type checker


def _filter_datasets(datasets: list[str], exclude_datasets: str | None) -> list[str]:
    if exclude_datasets:
        excluded = exclude_datasets.split(",") if exclude_datasets else []
        datasets = [dataset for dataset in datasets if dataset not in excluded]
        logger.info("Excluding datasets: %s", excluded)
        logger.info("Included datasets: %s", [dataset for dataset in datasets])
    return datasets


def _process_metrics_data(
    data: list[dict[str, Any]], dataset: str, reset_data: bool = False
) -> list[HttpRequestEntry | FirewallEventEntry]:
    """Process raw metrics data into the appropriate metric entry type."""
    processed_data: list[HttpRequestEntry | FirewallEventEntry] = []

    if reset_data:
        processed_data = []

    for entry in data:
        if dataset == "httpRequestsOverviewAdaptiveGroups":
            processed_data.append(
                {
                    "dimensions": {
                        "clientCountryName": entry["dimensions"]["clientCountryName"],
                        "edgeResponseStatus": entry["dimensions"]["edgeResponseStatus"],
                    },
                    "sum": {
                        "requests": entry["sum"]["requests"],
                        "bytes": entry["sum"]["bytes"],
                        "cachedRequests": entry["sum"]["cachedRequests"],
                        "cachedBytes": entry["sum"]["cachedBytes"],
                    },
                }
            )
        elif dataset == "firewallEventsAdaptiveGroups":
            processed_data.append(
                {
                    "dimensions": {
                        "action": entry["dimensions"]["action"],
                        "ruleId": entry["dimensions"]["ruleId"],
                        "source": entry["dimensions"]["source"],
                    },
                    "count": entry["count"],
                }
            )
        else:
            logger.warning(f"Unsupported dataset type: {dataset}")
            continue

    return processed_data


def cloudflare_fetch_metrics(
    account: Any, client: Any, config: CloudflareConfig, zones: list[str]
) -> None:
    """Fetch metrics from Cloudflare for all configured zones.

    Args:
        client: Cloudflare API client
        config: Application configuration dictionary
        zones: List of zone IDs to fetch metrics for
    """

    # Clean up old metrics after new ones are fetched
    COLLECTOR.cleanup_old_metrics()

    if config.cmb_region == "eu":
        datasets = [
            "httpRequestsOverviewAdaptiveGroups",
            "firewallEventsAdaptiveGroups",
            # We're unable to test account metrics at the moment
            # Error: "account 'XXX' does not have access to the path.
            # Refer to this page for more details about access controls:
            # https://developers.cloudflare.com/analytics/graphql-api/errors/
            # "dosdNetworkAnalyticsAdaptiveGroups",
            # "cdnNetworkAnalyticsAdaptiveGroups",
            # "warpDeviceAdaptiveGroups",
        ]
    else:
        datasets = [
            "dnsAnalyticsAdaptiveGroups",
            "firewallEventsAdaptiveGroups",
            "httpRequestsOverviewAdaptiveGroups",
            # We're unable to test account metrics at the moment
            # Error: "account 'XXX' does not have access to the path.
            # Refer to this page for more details about access controls:
            # https://developers.cloudflare.com/analytics/graphql-api/errors/
            # "dosdNetworkAnalyticsAdaptiveGroups",
            # "cdnNetworkAnalyticsAdaptiveGroups",
            # "warpDeviceAdaptiveGroups",
        ]

    free_datasets = ["httpRequestsOverviewAdaptiveGroups"]

    datasets = _filter_datasets(datasets, config.exclude_datasets)

    headers = {
        "Authorization": f"Bearer {config.api_token}",
        "Content-Type": "application/json",
    }

    current_time = datetime.now(UTC)
    timestamp_end = _rounddown_time(current_time)
    timestamp_start = _rounddown_time(
        current_time - timedelta(seconds=config.scrape_delay)
    )

    # Process dataset metrics
    for dataset in datasets:
        for zone in zones:

            zone_name = client.zones.get(zone_id=zone).name

            # Always returns free plan for some reason
            # plans = client.zones.plans.list(zone_id=zone)

            # Using subscription to check if the zone is on the free plan
            subscription = client.zones.subscriptions.get(zone)
            if (
                subscription["rate_plan"]["id"] == "cf_free"
                and dataset not in free_datasets
            ):
                logger.info(
                    f"Zone {zone_name} is on the free plan, skipping dataset: {dataset}"
                )
                continue

            logger.info(f"Fetching {dataset} metrics for zone: {zone_name}")

            query = _get_query(os.path.join("queries", f"{dataset}.gql"))

            # Determine the variables based on the dataset
            if dataset in [
                "httpRequestsOverviewAdaptiveGroups",
                "firewallEventsAdaptiveGroups",
            ]:
                variables = {
                    "zoneTag": zone,
                    "datetimeGeq": timestamp_start,
                    "datetimeLeq": timestamp_end,
                }
                logger.debug(f"Variables for {dataset}: {variables}")
            else:
                variables = {
                    "accountId": account.id,
                    "datetimeGeq": timestamp_start,
                    "datetimeLeq": timestamp_end,
                }

            payload = {
                "query": query,
                "variables": variables,
            }

            logger.debug(f"Querying {dataset} with variables: {variables}")

            try:
                response_json = _make_cloudflare_request(
                    config.api_url, headers, payload
                )

                # Log the full response for debugging
                logger.debug(f"Full response for {dataset}: {response_json}")

                if response_json.get("errors"):
                    logger.error(
                        f"GraphQL errors for zone {zone_name}: "
                        f"{response_json['errors']}"
                    )
                    continue

                data = response_json["data"]["viewer"]["zones"][0].get(dataset, [])

                # Log the response for debugging
                logger.debug(f"Response for {dataset} metrics: {data}")

                # Check if data is empty and log accordingly
                if not data:
                    logger.info(f"No data returned for {dataset} for zone: {zone_name}")
                    continue

                processed_data = _process_metrics_data(data, dataset)
                prometheus_generate_metrics(
                    processed_data,
                    zone_name,
                    timestamp_start,
                    None,
                    None,
                    None,
                    account.name,
                    account.id,
                )
                logger.info(
                    f"Metrics generated successfully for {dataset} "
                    f"for zone: {zone_name}"
                )

            except Exception as e:
                logger.error(
                    "Failed to process metrics",
                    extra={"dataset": dataset, "zone_name": zone_name, "error": str(e)},
                )

    # Fetch enterprise zones quota and usage
    try:
        max_quota = account.legacy_flags["enterprise_zone_quota"]["maximum"]
        current_quota = account.legacy_flags["enterprise_zone_quota"]["current"]
        available_quota = account.legacy_flags["enterprise_zone_quota"]["available"]

        prometheus_generate_metrics(
            None,  # Don't pass data for quota metrics
            None,  # Don't pass zone_name for quota metrics
            timestamp_start,
            max_quota,
            current_quota,
            available_quota,
            account.name,
            account.id,
        )
    except Exception as e:
        logger.error(
            "Failed to fetch enterprise zones quota and usage", extra={"error": str(e)}
        )
