from infra.observability.logger import log_event


def record_counter(name: str, value: int = 1, **labels) -> None:
    log_event("metric_counter", metric=name, value=value, **labels)
