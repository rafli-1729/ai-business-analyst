from warehouse.ingestion.registry import TABLE_REGISTRY


def resolve_target_schema(table_name: str) -> str:
    config = TABLE_REGISTRY.get(table_name)

    if not config:
        raise ValueError(
            f"No registry configuration for table: {table_name}"
        )

    return config["target_schema"]