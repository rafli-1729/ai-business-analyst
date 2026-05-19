import logging
import json
from pathlib import Path
import pandas as pd
from warehouse.ingestion.sources.base import BaseSource

logger = logging.getLogger(__name__)

with open("warehouse/ingestion/registry.json", "r") as f:
    TABLE_REGISTRY = json.load(f)

class GoogleSheetsSource(BaseSource):

    def __init__(
        self,
        spreadsheet_id: str,
        cache_dir: str = "data/google_sheets_cache",
    ):
        self.spreadsheet_id = spreadsheet_id
        self.cache_dir = Path(cache_dir)
        self.expectations_path = Path("warehouse/quality/expectations.json")

    def _load_expectations(self):
        if self.expectations_path.exists():
            with open(self.expectations_path, "r") as f:
                data = json.load(f)
                return data.get("expectations", {})
        return {}

    def fetch(self) -> Path:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        expectations = self._load_expectations()

        for table_name, config in TABLE_REGISTRY.items():
            if config["source_type"] != "google_sheets":
                continue

            local_path = self.cache_dir / f"{table_name}.csv"
            gid = config["sheet_gid"]
            export_url = f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/export?format=csv&gid={gid}"

            logger.info(f"Checking Google Sheet: {table_name}")

            # Download to memory first
            try:
                df_new = pd.read_csv(export_url)
                new_row_count = len(df_new)
            except Exception as e:
                logger.error(f"Failed to download {table_name}: {str(e)}")
                continue

            should_update = False

            if not local_path.exists():
                logger.info(f"Local cache not found for {table_name}. Initial download.")
                should_update = True
            else:
                # Check against expectations if available
                table_exp = expectations.get(table_name, {})
                expected_count = table_exp.get("row_count")

                if expected_count is not None and new_row_count > expected_count:
                    logger.info(f"New data detected for {table_name}: {new_row_count} rows (expected {expected_count}). Updating local cache.")
                    should_update = True
                elif expected_count is not None and new_row_count < expected_count:
                    logger.warning(f"Data for {table_name} has fewer rows ({new_row_count}) than expected ({expected_count}).")
                    # Still update local cache if you want current version, or stay with old one.
                    # Given the request "if file does not exist or there are additions", we update only if more rows.
                else:
                    logger.info(f"No new data detected for {table_name}. Skipping local cache update.")

            if should_update:
                df_new.to_csv(local_path, index=False)
                logger.info(f"Successfully updated local cache for {table_name}.")

        return self.cache_dir

    def list_csv_files(self, dataset_path: Path) -> list[Path]:
        return sorted(
            file
            for file in dataset_path.iterdir()
            if file.suffix == ".csv"
        )
