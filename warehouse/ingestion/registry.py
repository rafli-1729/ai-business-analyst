TABLE_REGISTRY = {
    "customers": {
        "source_type": "google_sheets",
        "target_schema": "bronze",
        "table_type": "dimension",
        "sheet_gid": "1213647959",
    },

    "geolocation": {
        "source_type": "kaggle",
        "target_schema": "reference",
        "table_type": "reference",
    },

    "products": {
        "source_type": "google_sheets",
        "target_schema": "bronze",
        "table_type": "dimension",
        "sheet_gid": "1490659044",
    },

    "sellers": {
        "source_type": "google_sheets",
        "target_schema": "bronze",
        "table_type": "dimension",
        "sheet_gid": "1046237413",
    },

    "product_category_name_translation": {
        "source_type": "kaggle",
        "target_schema": "reference",
        "table_type": "reference",
    },

    "order_items": {
        "source_type": "google_sheets",
        "target_schema": "bronze",
        "table_type": "fact",
        "sheet_gid": "1765416245",
    },

    "order_payments": {
        "source_type": "google_sheets",
        "target_schema": "bronze",
        "table_type": "fact",
        "sheet_gid": "1815706989",
    },

    "order_reviews": {
        "source_type": "google_sheets",
        "target_schema": "bronze",
        "table_type": "fact",
        "sheet_gid": "390056418",
    },

    "orders": {
        "source_type": "google_sheets",
        "target_schema": "bronze",
        "table_type": "fact",
        "sheet_gid": "591808341",
    },
}