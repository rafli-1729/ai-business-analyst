from dagster import Definitions, define_asset_job

from orchestration.dagster.assets.bronze_assets import bronze_olist_sources
from orchestration.dagster.assets.silver_assets import silver_warehouse
from orchestration.dagster.assets.gold_assets import gold_analytics_marts
from orchestration.dagster.assets.semantic_assets import semantic_catalog


warehouse_refresh_job = define_asset_job(name="warehouse_refresh")


defs = Definitions(
    assets=[
        bronze_olist_sources,
        silver_warehouse,
        gold_analytics_marts,
        semantic_catalog,
    ],
    jobs=[warehouse_refresh_job],
)
