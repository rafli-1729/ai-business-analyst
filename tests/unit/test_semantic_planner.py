from ai.services.schema_loader import load_schema_metadata
from ai.planners.semantic_planner import build_query_plan


def test_semantic_planner_selects_monthly_table_for_trend_question():
    plan = build_query_plan(
        "show monthly revenue trend",
        load_schema_metadata(),
    )

    assert plan.intent == "trend"
    assert plan.candidate_tables[0].name == "gold.monthly_revenue"


def test_semantic_planner_uses_semantic_columns_for_hints():
    plan = build_query_plan(
        "top product categories by revenue",
        load_schema_metadata(),
    )

    assert "total_revenue" in plan.metric_hints or "order_item_revenue" in plan.metric_hints
    assert "product_category_name" in plan.dimension_hints
