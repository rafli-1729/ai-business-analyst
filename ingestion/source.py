import os
from pathlib import Path

import kagglehub


def download_dataset(dataset_slug: str) -> Path:
    return Path(kagglehub.dataset_download(dataset_slug))


def list_csv_files(dataset_path: Path) -> list[Path]:
    return sorted(
        dataset_path / file_name
        for file_name in os.listdir(dataset_path)
        if file_name.endswith(".csv")
    )


def table_name_from_source_file(path: Path) -> str:
    return (
        path.name
        .replace(".csv", "")
        .replace("olist_", "")
        .replace("_dataset", "")
    )


def estimate_csv_rows(path: Path) -> int:
    with path.open(encoding="utf-8") as file:
        return max(sum(1 for _ in file) - 1, 0)
