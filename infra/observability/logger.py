import logging
import sys
import time

def setup_logging():
    """Configures a standardized logger with high-precision timestamps."""
    log_formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    root_logger = logging.getLogger()

    # Clear existing handlers
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    root_logger.setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return root_logger


def log_event(event_name: str, **kwargs):
    """Logs an application event with metadata."""
    logger = logging.getLogger("app.events")
    metadata = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.info(f"EVENT: {event_name} | {metadata}")
