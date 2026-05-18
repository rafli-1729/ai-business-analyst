import sqlalchemy
from warehouse.ingestion.config import load_ingestion_config
import logging

logger = logging.getLogger(__name__)

def run_warehouse_tests():
    config = load_ingestion_config()
    engine = sqlalchemy.create_engine(config.database_url)
    
    logger.info("Starting Warehouse Quality Tests")
    
    # 1. Test: Ensure critical schemas exist
    schemas = ['bronze', 'silver', 'gold', 'ops']
    with engine.connect() as conn:
        for schema in schemas:
            res = conn.execute(sqlalchemy.text(f"SELECT count(*) FROM information_schema.schemata WHERE schema_name = '{schema}'"))
            if res.scalar() == 0:
                logger.error(f"Schema '{schema}' missing.")
            else:
                logger.info(f"Schema '{schema}' exists.")

    # 2. Test: Check for tables in bronze
    with engine.connect() as conn:
        res = conn.execute(sqlalchemy.text("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'bronze'"))
        count = res.scalar()
        if count > 0:
            logger.info(f"PASSED: Found {count} tables in bronze schema.")
        else:
            logger.warning("No tables found in bronze schema.")

    logger.info("Warehouse Tests Complete")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_warehouse_tests()
