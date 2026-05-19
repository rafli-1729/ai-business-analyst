from warehouse.ingestion.config import load_ingestion_config
from warehouse.ingestion.loader import BronzeIngestor
from warehouse.ingestion.sources.local_seed import LocalSeedSource
from warehouse.quality.checks import IngestionValidator
from infra.observability.logger import setup_logging
import logging
import sys
import os
from pathlib import Path

logger = setup_logging()

import json

def load_reference_seeds(ingestor):
    """Load seed files from warehouse/transformation/seeds to the appropriate schema (reference/master)."""
    logger.info("Loading reference seeds into database...")
    seed_source = LocalSeedSource()
    seeds = seed_source.list_csv_files(Path("."))

    with open("warehouse/ingestion/registry.json", "r") as f:
        registry = json.load(f)

    for seed_path in seeds:
        table_name = seed_path.stem
        config = registry.get(table_name)
        
        if not config:
            logger.warning(f"Skipping seed {table_name}: not found in registry.")
            continue
            
        target_schema = config.get("target_schema", "reference")
        
        # Ingest into the appropriate schema
        ingestor.ingest_file(
            source_path=seed_path,
            table_name=table_name,
            target_schema=target_schema,
            total_rows=0 # No strict row count needed for seeds
        )
    logger.info("Reference seeds loaded.")

def run_ingestion_with_validation():
    config = load_ingestion_config()
    ingestor = BronzeIngestor(config)

    # 1. Load Reference Seeds First
    load_reference_seeds(ingestor)

    # 2. Ingest Dataset
    validator = IngestionValidator(ingestor.engine)

    results = ingestor.ingest_dataset()

    # ... remaining logic ...

    all_passed = True
    for result in results:
        if result.status == "success":
            validation = validator.validate_table(result.target_table, schema=result.target_schema)
            if validation.get("passed"):
                logger.info(f"✅ Validation PASSED for {result.target_table}")
            else:
                logger.error(f"❌ Validation FAILED for {result.target_table}: {validation}")
                all_passed = False
        elif result.status == "skipped":
            logger.info(f"⏩ Skipped validation for {result.target_table} (already ingested)")

    if not all_passed:
        logger.error("Pipeline failed due to validation errors.")
        sys.exit(1)

if __name__ == "__main__":
    run_ingestion_with_validation()
