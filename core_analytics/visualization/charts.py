import pandas as pd

def infer_chart_type(df: pd.DataFrame) -> str:
    """Infer a basic chart type based on the dataframe structure."""
    if df.empty:
        return "table"
        
    cols = df.columns
    if len(cols) >= 2:
        # If we have a numeric column and a categorical/time column
        # very basic heuristic
        return "bar"
        
    return "table"
