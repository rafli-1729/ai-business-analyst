-- Silver Products: Normalized & Incremental Upsert (Join-based)
CREATE UNLOGGED TABLE IF NOT EXISTS silver.products (
    product_id TEXT PRIMARY KEY,
    product_category_name TEXT,
    product_name_length INTEGER,
    product_description_length INTEGER,
    product_photos_qty INTEGER,
    product_weight_g NUMERIC,
    product_length_cm NUMERIC,
    product_height_cm NUMERIC,
    product_width_cm NUMERIC,
    _last_updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Temp table for processing
CREATE TEMP TABLE stg_products_cleaned AS
SELECT
    NULLIF(TRIM(b.product_id::TEXT), '') AS product_id,
    COALESCE(cm.canonical_category, TRIM(b.product_category_name::TEXT)) AS product_category_name,
    NULLIF(TRIM(b.product_name_lenght::TEXT), '')::NUMERIC::INTEGER AS product_name_length,
    NULLIF(TRIM(b.product_description_lenght::TEXT), '')::NUMERIC::INTEGER AS product_description_length,
    NULLIF(TRIM(b.product_photos_qty::TEXT), '')::NUMERIC::INTEGER AS product_photos_qty,
    NULLIF(TRIM(b.product_weight_g::TEXT), '')::NUMERIC AS product_weight_g,
    NULLIF(TRIM(b.product_length_cm::TEXT), '')::NUMERIC AS product_length_cm,
    NULLIF(TRIM(b.product_height_cm::TEXT), '')::NUMERIC AS product_height_cm,
    NULLIF(TRIM(b.product_width_cm::TEXT), '')::NUMERIC AS product_width_cm
FROM bronze.products b
LEFT JOIN reference.product_category_mapping cm 
    ON TRIM(b.product_category_name) = cm.raw_category;

INSERT INTO silver.products (
    product_id,
    product_category_name,
    product_name_length,
    product_description_length,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm,
    _last_updated_at
)
SELECT 
    product_id,
    product_category_name,
    product_name_length,
    product_description_length,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm,
    NOW()
FROM stg_products_cleaned
ON CONFLICT (product_id) 
DO UPDATE SET
    product_category_name = EXCLUDED.product_category_name,
    product_name_length = EXCLUDED.product_name_length,
    product_description_length = EXCLUDED.product_description_length,
    product_photos_qty = EXCLUDED.product_photos_qty,
    product_weight_g = EXCLUDED.product_weight_g,
    product_length_cm = EXCLUDED.product_length_cm,
    product_height_cm = EXCLUDED.product_height_cm,
    product_width_cm = EXCLUDED.product_width_cm,
    _last_updated_at = NOW();

CREATE INDEX IF NOT EXISTS idx_silver_products_category ON silver.products(product_category_name);

COMMENT ON TABLE silver.products IS 'Cleaned product dimension table with normalized categories.';
COMMENT ON COLUMN silver.products.product_id IS 'Primary Key. Unique identifier for the product.';
COMMENT ON COLUMN silver.products.product_category_name IS 'Category name normalized to English. Format: snake_case (e.g., "health_beauty").';
COMMENT ON COLUMN silver.products.product_name_length IS 'Number of characters in the product name.';
COMMENT ON COLUMN silver.products.product_description_length IS 'Number of characters in the product description.';
COMMENT ON COLUMN silver.products.product_photos_qty IS 'Number of photos in the product listing.';
COMMENT ON COLUMN silver.products.product_weight_g IS 'Product weight in grams.';
COMMENT ON COLUMN silver.products.product_length_cm IS 'Product length in centimeters.';
COMMENT ON COLUMN silver.products.product_height_cm IS 'Product height in centimeters.';
COMMENT ON COLUMN silver.products.product_width_cm IS 'Product width in centimeters.';
