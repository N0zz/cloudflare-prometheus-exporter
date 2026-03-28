import logging
import sys
from datetime import UTC, datetime
from typing import Any

from dotenv import load_dotenv
from pythonjsonlogger.json import JsonFormatter

load_dotenv()


class CustomJsonFormatter(JsonFormatter):
    """Custom JSON formatter with additional fields."""

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        """Add custom fields to the log record."""
        super().add_fields(log_record, record, message_dict)

        # Rename fields for better clarity
        log_record["level"] = record.levelname
        log_record["timestamp"] = datetime.fromtimestamp(
            record.created, UTC
        ).isoformat()

        # Add additional context
        log_record["logger"] = record.name
        log_record["function"] = record.funcName

        # Remove fields we've renamed
        log_record.pop("levelname", None)
        log_record.pop("asctime", None)


def setup_logger(log_level: str) -> logging.Logger:
    """Set up a configured logger instance."""
    logger = logging.getLogger("cloudflare_exporter")

    # Validate log level
    try:
        log_level = log_level.upper()
        numeric_level = getattr(logging, log_level)
    except (AttributeError, TypeError) as e:
        raise ValueError(
            f"Invalid log level: {log_level}. "
            "Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
        ) from e

    # If logger already exists and is configured, return it
    if logger.handlers:
        return logger

    # Set up new logger
    logger.setLevel(numeric_level)

    # Create formatter
    formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s", json_ensure_ascii=False
    )

    # Set up stdout handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger
