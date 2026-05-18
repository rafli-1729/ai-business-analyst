import logging
import json
from pathlib import Path
import pandas as pd
from warehouse.ingestion.sources.base import BaseSource

logger = logging.getLogger(__name__)

with open("warehouse/ingestion/registry.json", "r") as f:
    TABLE_REGISTRY = json.load(f)

class LocalSeedSource(BaseSource):
    """Source for local CSV seeds generated during the process."""
    
    def __init__(self):
        pass

    def fetch(self) -> Path:
        # For local seeds, we don't 'fetch' from internet, 
        # but we return a virtual path or just confirm they exist.
        # We'll return the root so list_csv_files can find them.
        return Path(".")

    def list_csv_files(self, dataset_path: Path) -> list[Path]:
        files = []
        for table_name, config in TABLE_REGISTRY.items():
            if config.get("source_type") == "local_seed":
                path = Path(config["local_path"])
                if path.exists():
                    files.append(path)
                else:
                    logger.warning(f"Local seed for {table_name} not found at {path}")
        return files
