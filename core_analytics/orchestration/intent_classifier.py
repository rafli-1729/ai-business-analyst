"""
Intent Classifier for the Olist Agent Analyst.
Provides unique keyword-based classification for domain agents.
"""

# Unique Keywords for each agent to prevent overlap
AGENT_KEYWORDS = {
    "sales": {
        "revenue", "sales", "transaction", "income", "gmv", "omzet", 
        "penjualan", "pendapatan", "keuntungan", "profit", "money", 
        "duit", "cuan", "financial", "keuangan", "avg_order_value", "aov"
    },
    "ops": {
        "delivery", "shipping", "freight", "logistics", "pengiriman", 
        "logistik", "kurir", "fulfillment", "estimasi", "late", "ontime", 
        "shipping_cost", "freight_value", "delay"
    },
    "customer": {
        "customer", "buyer", "user", "consumer", "pembeli", "pelanggan", 
        "demographic", "demografi", "persona", "profiling", "gender", "age"
    },
    "product": {
        "product", "category", "item", "sku", "barang", "produk", 
        "kategori", "inventory", "stok", "volume", "weight"
    },
    "geo": {
        "city", "state", "region", "location", "geography", "map", 
        "kota", "wilayah", "lokasi", "geografis", "uf", "zip code"
    },
    "retention": {
        "churn", "retention", "repeat", "loyalty", "loyalitas", 
        "churn rate", "pembelian berulang", "frequency"
    },
    "trend": {
        "trend", "growth", "increase", "decrease", "monthly", 
        "yearly", "seasonal", "pertumbuhan", "kenaikan", "penurunan",
        "tahunan", "bulanan", "grafik", "timeline", "over time"
    },
    "ranker": {
        "top", "best", "highest", "lowest", "rank", "terbaik", 
        "teratas", "terbawah", "paling", "peringkat", "leaderboard"
    },
    "diagnostic": {
        "why", "reason", "cause", "driver", "impact", "mengapa", 
        "kenapa", "alasan", "penyebab", "analisa", "diagnosa", "correlation"
    }
}

def classify_intent_by_keywords(question: str) -> str | None:
    """
    Classifies intent based on priority keywords with rigid matching.
    """
    normalized = f" {question.lower()} " # Pad with spaces for word-like matching
    
    # Priority order: Sales and Ops first as they are the most common domain drivers
    priority_order = [
        "sales", "ops", "retention", "customer", "geo", "product", 
        "diagnostic", "trend", "ranker"
    ]
    
    for agent_key in priority_order:
        keywords = AGENT_KEYWORDS.get(agent_key, set())
        for kw in keywords:
            # Check for keyword with surrounding spaces or at start/end
            if f" {kw} " in normalized or normalized.startswith(f"{kw} ") or normalized.endswith(f" {kw}"):
                return agent_key
            
    return None

def classify_intent(question: str) -> str:
    """Legacy wrapper for backward compatibility."""
    res = classify_intent_by_keywords(question)
    return res if res else "general"
