import pandas as pd
from typing import Any

def dataframe_to_rows(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert a pandas DataFrame to a list of dictionaries (rows)."""
    return df.to_dict(orient="records")

