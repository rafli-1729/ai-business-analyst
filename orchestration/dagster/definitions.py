from dagster import asset, Definitions, AssetIn, Output
from warehouse.ingestion.loader import BronzeIngestor
from warehouse.ingestion.config import load_ingestion_config
from warehouse.quality.checks import IngestionValidator
import logging
import json

logger = logging.getLogger(__name__)

with open("warehouse/ingestion/registry.json", "r") as f:
    TABLE_REGISTRY = json.load(f)

def create_ingestion_asset(table_name: str):
    @asset(name=f"ingested_{table_name}", group_name="ingestion")
    def ingestion_asset():
        config = load_ingestion_config()
        ingestor = BronzeIngestor(config)
        
        # Find the source path for this table from the ingestor's plan
        plan = ingestor._build_ingestion_plan()
        table_plan = next((p for p in plan if p["table_name"] == table_name), None)
        
        if not table_plan:
            raise ValueError(f"Table {table_name} not found in ingestion plan")
            
        result = ingestor.ingest_file(
            source_path=table_plan["source_path"],
            table_name=table_name,
            target_schema=table_plan["target_schema"],
            total_rows=table_plan["total_rows"]
        )
        
        # VALIDATION STEP
        validator = IngestionValidator(ingestor.engine)
        validation_results = validator.validate_table(table_name, schema=table_plan["target_schema"])
        
        if not validation_results.get("passed", True):
            logger.error(f"Validation FAILED for {table_name}: {validation_results}")
            raise ValueError(f"Data validation failed for {table_name}")
            
        logger.info(f"Validation PASSED for {table_name}")
        return validation_results

    return ingestion_asset

# Register assets for all tables in the registry
from warehouse.ingestion.registry import TABLE_REGISTRY
ingestion_assets = [create_ingestion_asset(table_name) for table_name in TABLE_REGISTRY.keys()]

defs = Definitions(
    assets=ingestion_assets
)
