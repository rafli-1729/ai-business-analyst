from contextlib import contextmanager

from infra.observability.logger import timed


@contextmanager
def trace_span(name: str, **attributes):
    with timed(name, **attributes):
        yield
