from dagster import AssetExecutionContext, MaterializeResult, MetadataValue, asset

from warehouse.semantic.catalog import SemanticCatalog


@asset(group_name="semantic", compute_kind="python", deps=["gold_analytics_marts"])
def semantic_catalog(context: AssetExecutionContext) -> MaterializeResult:
    catalog = SemanticCatalog()
    analytics_tables = catalog.analytics_tables()

    context.log.info("Loaded semantic catalog version %s", catalog.schema_version())

    return MaterializeResult(
        metadata={
            "schema_version": catalog.schema_version(),
            "analytics_table_count": len(analytics_tables),
            "relationships": MetadataValue.json(catalog.relationships()),
        }
    )
