import json
import logging
import time
import uuid
from contextlib import contextmanager


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("ai_business_analyst")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    return logger


logger = setup_logger()


def new_request_id() -> str:
    return str(uuid.uuid4())


def log_event(event: str, **kwargs) -> None:
    payload = {"event": event, "ts": int(time.time() * 1000), **kwargs}
    logger.info(json.dumps(payload, default=str))


@contextmanager
def timed(event: str, **kwargs):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        log_event(event, elapsed_ms=elapsed_ms, **kwargs)
