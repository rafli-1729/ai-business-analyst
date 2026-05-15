from pathlib import Path

import pandas as pd

from warehouse.ingestion.registry import TABLE_REGISTRY
from warehouse.ingestion.sources.base import BaseSource


class GoogleSheetsSource(BaseSource):

    def __init__(
        self,
        spreadsheet_id: str,
        cache_dir: str = "data/google_sheets_cache",
    ):
        self.spreadsheet_id = spreadsheet_id
        self.cache_dir = Path(cache_dir)

    def fetch(self) -> Path:

        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        for table_name, config in TABLE_REGISTRY.items():

            if config["source_type"] != "google_sheets":
                continue

            gid = config["sheet_gid"]

            export_url = (
                f"https://docs.google.com/spreadsheets/d/"
                f"{self.spreadsheet_id}/export"
                f"?format=csv&gid={gid}"
            )

            print(
                f"Downloading Google Sheet: {table_name}"
            )

            df = pd.read_csv(export_url)

            df.to_csv(
                self.cache_dir / f"{table_name}.csv",
                index=False,
            )

        return self.cache_dir

    def list_csv_files(
        self,
        dataset_path: Path,
    ) -> list[Path]:

        return sorted(
            file
            for file in dataset_path.iterdir()
            if file.suffix == ".csv"
        )