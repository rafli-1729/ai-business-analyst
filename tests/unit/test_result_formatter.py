import pandas as pd

from core_analytics.analytics.result_formatter import dataframe_to_rows
from core_analytics.visualization.charts import infer_chart_type


def test_dataframe_to_rows_replaces_nan_with_none():
    dataframe = pd.DataFrame([{"name": "health", "value": None}])

    assert dataframe_to_rows(dataframe) == [{"name": "health", "value": None}]


def test_infer_chart_type_uses_line_for_date_first_column():
    dataframe = pd.DataFrame(
        [
            {"purchase_month": "2018-01", "revenue": 100},
            {"purchase_month": "2018-02", "revenue": 120},
        ]
    )

    assert infer_chart_type(dataframe) == "line"


def test_infer_chart_type_uses_bar_for_categorical_numeric_data():
    dataframe = pd.DataFrame(
        [
            {"category": "health", "revenue": 100},
            {"category": "watches", "revenue": 120},
        ]
    )

    assert infer_chart_type(dataframe) == "bar"
