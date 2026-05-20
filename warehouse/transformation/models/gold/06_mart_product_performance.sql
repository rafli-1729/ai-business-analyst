-- Mart: Product Performance
-- Grain: One row per product
-- Purpose: Analyzing product popularity, revenue generation, and customer satisfaction.

CREATE UNLOGGED TABLE IF NOT EXISTS gold.mart_product_performance (
    product_id TEXT PRIMARY KEY,
    product_category_name TEXT,
    total_revenue NUMERIC,
    total_units_sold INTEGER,
    avg_price NUMERIC,
    avg_review_score NUMERIC,
    total_photos INTEGER,
    product_weight_g NUMERIC,
    _last_updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transformation logic
CREATE TEMP TABLE stg_product_performance AS
WITH product_metrics AS (
    SELECT 
        oi.product_id,
        SUM(oi.price) as total_revenue,
        COUNT(*) as total_units_sold,
        AVG(oi.price) as avg_price
    FROM silver.order_items oi
    JOIN silver.orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1
),
product_reviews AS (
    SELECT 
        oi.product_id,
        AVG(r.review_score) as avg_review_score
    FROM silver.order_items oi
    JOIN silver.order_reviews r ON oi.order_id = r.order_id
    GROUP BY 1
)
SELECT 
    p.product_id,
    p.product_category_name,
    COALESCE(m.total_revenue, 0) as total_revenue,
    COALESCE(m.total_units_sold, 0) as total_units_sold,
    COALESCE(m.avg_price, 0) as avg_price,
    COALESCE(r.avg_review_score, 0) as avg_review_score,
    p.product_photos_qty as total_photos,
    p.product_weight_g
FROM silver.products p
LEFT JOIN product_metrics m ON p.product_id = m.product_id
LEFT JOIN product_reviews r ON p.product_id = r.product_id;

-- Upsert
INSERT INTO gold.mart_product_performance (
    product_id, product_category_name, total_revenue, total_units_sold,
    avg_price, avg_review_score, total_photos, product_weight_g, _last_updated_at
)
SELECT *, NOW() FROM stg_product_performance
ON CONFLICT (product_id) DO UPDATE SET
    total_revenue = EXCLUDED.total_revenue,
    total_units_sold = EXCLUDED.total_units_sold,
    avg_review_score = EXCLUDED.avg_review_score,
    _last_updated_at = NOW();

-- Column Comments
COMMENT ON TABLE gold.mart_product_performance IS 'Product performance mart. Use this for ranking products, analyzing category trends, and correlation between photos/weight and sales. Grain: One row per product.';
COMMENT ON COLUMN gold.mart_product_performance.product_id IS 'Primary Key. Unique identifier for the product.';
COMMENT ON COLUMN gold.mart_product_performance.product_category_name IS 'Normalized category name of the product in English.';
COMMENT ON COLUMN gold.mart_product_performance.total_revenue IS 'Total product revenue generated (excluding freight) for delivered orders.';
COMMENT ON COLUMN gold.mart_product_performance.total_units_sold IS 'Total quantity of this product sold.';
COMMENT ON COLUMN gold.mart_product_performance.avg_price IS 'Average unit price of the product across all sales.';
COMMENT ON COLUMN gold.mart_product_performance.avg_review_score IS 'Average customer review score for this product.';
COMMENT ON COLUMN gold.mart_product_performance.total_photos IS 'Number of product photos uploaded to the catalog.';
COMMENT ON COLUMN gold.mart_product_performance.product_weight_g IS 'Weight of the product in grams.';
