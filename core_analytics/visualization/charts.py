import pandas as pd
from typing import Dict, Any, List, Optional

def infer_chart_type(df: pd.DataFrame) -> str:
    """Infer a basic chart type based on the dataframe structure."""
    if df.empty:
        return "table"
        
    cols = df.columns
    if len(cols) >= 2:
        first_col = cols[0]
        # Heuristic for line chart: first column name contains date/time/month or first value looks like date
        first_val = str(df.iloc[0, 0]) if not df.empty else ""
        if any(kw in first_col.lower() for kw in ["date", "time", "month", "year", "day", "tahun", "bulan"]) or "-" in first_val and len(first_val) >= 7:
            return "line"
        return "bar"
        
    return "table"

def prepare_chart_data(df: pd.DataFrame, custom_config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Intelligently prepares data for the ChartRenderer.
    If custom_config is provided by the agent, it merges it with the data.
    """
    if df.empty or len(df.columns) < 2:
        return None

    # If the agent provided a full custom config, use it but inject the data
    if custom_config:
        # Ensure it has the necessary keys
        spec = custom_config.copy()
        spec["data"] = df.to_dict(orient="records")
        # Default to first column if xAxisKey not provided
        if "xAxisKey" not in spec:
            spec["xAxisKey"] = df.columns[0]
        # Default to other columns if yAxisKey not provided
        if "yAxisKey" not in spec:
            spec["yAxisKey"] = df.columns[1].tolist() if len(df.columns) > 2 else df.columns[1]
        return spec

    cols = list(df.columns)
    
    # 1. Identify column types
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = [c for c in cols if c not in numeric_cols]
    
    if not numeric_cols:
        return None

    chart_type = infer_chart_type(df)
    
    # Case A: 3 Columns (e.g., Year, Category, Value) -> Multi-series
    if len(categorical_cols) >= 2 and len(numeric_cols) == 1:
        x_axis = categorical_cols[0]
        pivot_col = categorical_cols[1]
        metric = numeric_cols[0]
        
        # Pivot the data: Rows=Year, Cols=State, Values=Revenue
        pivoted = df.pivot_table(index=x_axis, columns=pivot_col, values=metric, aggfunc='sum').reset_index()
        pivoted = pivoted.fillna(0)
        
        # New Y-axis keys are the unique values from the pivot column
        y_axis_keys = [c for c in pivoted.columns if c != x_axis]
        
        return {
            "type": chart_type,
            "data": pivoted.to_dict(orient="records"),
            "xAxisKey": x_axis,
            "yAxisKey": y_axis_keys,
            "title": f"{metric} by {x_axis} and {pivot_col}"
        }

    # Case B: 2 Columns (Standard X, Y)
    if len(cols) == 2:
        return {
            "type": chart_type,
            "data": df.to_dict(orient="records"),
            "xAxisKey": cols[0],
            "yAxisKey": cols[1],
            "title": f"{cols[1]} by {cols[0]}"
        }

    # Case C: Multiple metrics for one dimension (e.g., Date, Revenue, Orders)
    if len(categorical_cols) == 1 and len(numeric_cols) > 1:
        return {
            "type": chart_type,
            "data": df.to_dict(orient="records"),
            "xAxisKey": categorical_cols[0],
            "yAxisKey": numeric_cols,
            "title": "Multi-metric Analysis"
        }

    # Default fallback
    return {
        "type": chart_type,
        "data": df.to_dict(orient="records"),
        "xAxisKey": cols[0],
        "yAxisKey": cols[1] if len(cols) > 1 else cols[0],
        "title": "Data Visualization"
    }
