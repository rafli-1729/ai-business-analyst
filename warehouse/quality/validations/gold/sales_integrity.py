from sqlalchemy import text
from typing import Dict, Any

def validate_sales_integrity(engine) -> Dict[str, Any]:
    """Validates that Silver (total revenue) matches Gold (total revenue)."""
    query = text("""
        WITH silver_revenue AS (
            SELECT SUM(price + freight_value) as total_rev FROM silver.order_items
        ),
        gold_revenue AS (
            SELECT SUM(total_value) as total_rev FROM gold.fact_sales_items
        )
        SELECT 
            s.total_rev as silver_rev, 
            g.total_rev as gold_rev,
            ABS(s.total_rev - g.total_rev) as diff
        FROM silver_revenue s, gold_revenue g
    """)
    with engine.connect() as conn:
        res = conn.execute(query).fetchone()
        passed = res[2] < 0.01 # Tolerance for float precision
        return {
            "validation_name": "sales_integrity_silver_gold",
            "layer_name": "gold",
            "passed": passed,
            "issue_count": 0 if passed else 1
        }
