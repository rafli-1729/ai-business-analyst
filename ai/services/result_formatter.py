from typing import Any

import pandas as pd


def dataframe_to_rows(
    dataframe: pd.DataFrame,
    limit: int = 100
) -> list[dict[str, Any]]:
    if dataframe.empty:
        return []

    preview = dataframe.head(limit).astype(object)
    preview = preview.where(pd.notnull(preview), None)
    return preview.to_dict(orient="records")


def infer_chart_type(
    dataframe: pd.DataFrame
) -> str:
    if dataframe.empty or len(dataframe.columns) < 2:
        return "table"

    columns = list(dataframe.columns)
    first_column = columns[0].lower()
    numeric_columns = dataframe.select_dtypes(include="number").columns

    if len(numeric_columns) == 0:
        return "table"

    if any(token in first_column for token in ("date", "month", "year", "week", "day")):
        return "line"

    return "bar"
