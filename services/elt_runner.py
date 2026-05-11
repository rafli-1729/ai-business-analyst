from pathlib import Path

from models.warehouse import EltConfig
from warehouse.elt_runner import run_elt as run_layered_elt


SQL_ROOT = Path(__file__).resolve().parent.parent / "sql"


def run_elt(database_url: str, sql_dir: Path | None = None) -> dict:
    sql_root = sql_dir.parent if sql_dir and sql_dir.name == "elt" else (sql_dir or SQL_ROOT)
    return run_layered_elt(EltConfig(database_url=database_url, sql_root=sql_root))
