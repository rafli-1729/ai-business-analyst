from contextlib import contextmanager

from services.observability import timed


@contextmanager
def trace_span(name: str, **attributes):
    with timed(name, **attributes):
        yield
