import os
from pathlib import Path

import kagglehub

from warehouse.ingestion.sources.base import BaseSource


class KaggleSource(BaseSource):

    def __init__(self, dataset_slug: str):
        self.dataset_slug = dataset_slug

    def fetch(self) -> Path:
        return Path(
            kagglehub.dataset_download(self.dataset_slug)
        )

    def list_csv_files(self, dataset_path: Path) -> list[Path]:
        return sorted(
            dataset_path / file_name
            for file_name in os.listdir(dataset_path)
            if file_name.endswith(".csv")
        )