MART_MAPPINGS = {
    "trend": [
        "gold.sales_summary",
        "gold.review_summary",
    ],
    "ranking": [
        "gold.seller_performance",
        "gold.category_sales",
    ],
    "diagnostic": [
        "gold.sales_summary",
        "gold.category_sales",
        "gold.delivery_metrics",
        "gold.review_summary",
    ],
}


def select_marts(intent: str) -> list[str]:

    return MART_MAPPINGS.get(
        intent,
        ["gold.sales_summary"],
    )