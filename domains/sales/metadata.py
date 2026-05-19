"""
Sales domain metadata and semantic definitions.
"""

SALES_METRICS = {
    "total_revenue": "Sum of all order items price and freight_value.",
    "order_count": "Total number of distinct orders.",
    "average_order_value": "Total revenue divided by order count."
}

SALES_DIMENSIONS = [
    "order_status",
    "product_category",
    "seller_state"
]

def get_sales_context() -> str:
    """Returns semantic context specifically for sales analysis."""
    context = "Sales Metrics Definitions:\n"
    for metric, desc in SALES_METRICS.items():
        context += f"- {metric}: {desc}\n"
    context += f"\nCommon Sales Dimensions: {', '.join(SALES_DIMENSIONS)}\n"
    return context
