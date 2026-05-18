from pathlib import Path
from typing import Dict, Optional

from warehouse.transformation.engine.elt_runner import EltConfig, run_elt


def run_warehouse_elt(
    database_url: str,
    sql_root: Optional[Path] = None,
) -> Dict:
    root = sql_root or (
        Path(__file__).resolve().parents[2]
        / "warehouse"
        / "transformation"
        / "models"
    )

    return run_elt(
        EltConfig(
            database_url=database_url,
            sql_root=root,
        )
    )