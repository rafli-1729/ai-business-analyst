"""
Geography domain metadata and semantic definitions.
"""

GEOGRAPHY_DIMENSIONS = {
    "customer_state": "Categorical (Brazilian UF code, e.g., SP, RJ, MG)",
    "seller_state": "Categorical (Brazilian UF code)",
    "customer_city": "Canonical UTF-8 city name",
}

def get_geography_context() -> str:
    """Returns semantic context specifically for geographic analysis."""
    context = "Geographic Semantic Definitions:\n"
    for dim, desc in GEOGRAPHY_DIMENSIONS.items():
        context += f"- {dim}: {desc}\n"
    return context
