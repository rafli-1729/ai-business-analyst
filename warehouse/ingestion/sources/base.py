from abc import ABC, abstractmethod
from pathlib import Path


class BaseSource(ABC):

    @abstractmethod
    def fetch(self) -> Path:
        pass

    @abstractmethod
    def list_csv_files(self, dataset_path: Path) -> list[Path]:
        pass