import json
import logging
from datetime import datetime
from io import StringIO

import pytest

from cloudflare_exporter.logger import CustomJsonFormatter, setup_logger


@pytest.fixture
def log_output() -> tuple[logging.Logger, StringIO]:
    """Fixture providing a string buffer for capturing log output."""
    string_buffer = StringIO()
    handler = logging.StreamHandler(string_buffer)
    formatter = CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
    handler.setFormatter(formatter)

    logger = logging.getLogger("test_logger")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger, string_buffer


def test_custom_json_formatter(log_output: tuple[logging.Logger, StringIO]) -> None:
    """Test CustomJsonFormatter adds correct fields."""
    logger, string_buffer = log_output
    test_message = "Test log message"

    logger.info(test_message)
    log_entry = json.loads(string_buffer.getvalue())

    assert log_entry["level"] == "INFO"
    assert "timestamp" in log_entry
    assert log_entry["logger"] == "test_logger"
    assert log_entry["message"] == test_message
    assert "function" in log_entry

    # Verify renamed/removed fields
    assert "levelname" not in log_entry
    assert "asctime" not in log_entry

    # Verify timestamp format
    datetime.fromisoformat(log_entry["timestamp"])  # Should not raise exception


def test_setup_logger_basic() -> None:
    """Test basic logger setup."""
    logger = setup_logger("INFO")

    assert logger.name == "cloudflare_exporter"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    assert isinstance(logger.handlers[0].formatter, CustomJsonFormatter)
    assert not logger.propagate


def test_setup_logger_invalid_level() -> None:
    """Test setup_logger with invalid log level."""
    # Reset logger between tests
    logging.getLogger("cloudflare_exporter").handlers = []

    with pytest.raises(ValueError) as exc_info:
        setup_logger("INVALID_LEVEL")  # Use clearly invalid level
    assert "Invalid log level" in str(exc_info.value)


@pytest.fixture(autouse=True)
def reset_logger() -> None:  # type: ignore[misc]
    """Reset logger before each test."""
    logger = logging.getLogger("cloudflare_exporter")
    logger.handlers = []
    logger.level = logging.NOTSET
    logger.propagate = True
    yield
    # Clean up after test
    logger.handlers = []
    logger.level = logging.NOTSET
    logger.propagate = True


def test_setup_logger_case_insensitive(reset_logger: None) -> None:
    """Test setup_logger handles case-insensitive log levels."""
    logger_debug = setup_logger("debug")
    assert logger_debug.level == logging.DEBUG


def test_setup_logger_singleton(reset_logger: None) -> None:
    """Test setup_logger returns same logger instance."""
    logger1 = setup_logger("INFO")
    assert logger1.level == logging.INFO

    logger2 = setup_logger("DEBUG")  # Should return same instance, not change level
    assert logger1 is logger2
    assert logger1.level == logging.INFO  # Level should not change
