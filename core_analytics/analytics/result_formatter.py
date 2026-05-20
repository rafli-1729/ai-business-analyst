import pandas as pd
import numpy as np
from typing import Any

def dataframe_to_rows(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert a pandas DataFrame to a list of dictionaries (rows),
    ensuring values are JSON-compliant (handling NaN and Inf)."""
    
    # Replace NaN, Inf, and -Inf with None (which becomes null in JSON)
    sanitized_df = df.replace([np.inf, -np.inf], np.nan).where(pd.notnull(df), None)
    
    return sanitized_df.to_dict(orient="records")
