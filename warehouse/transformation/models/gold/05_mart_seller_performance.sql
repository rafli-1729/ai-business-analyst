-- Mart: Seller Performance
-- Grain: One row per seller
-- Purpose: Analyzing seller revenue, reliability, and geographic distribution.

CREATE UNLOGGED TABLE IF NOT EXISTS gold.mart_seller_performance (
    seller_id TEXT PRIMARY KEY,
    seller_city TEXT,
    seller_state TEXT,
    total_revenue NUMERIC,
    total_orders INTEGER,
    total_items_sold INTEGER,
    avg_item_price NUMERIC,
    avg_review_score NUMERIC,
    late_delivery_rate NUMERIC,
    active_since TIMESTAMP,
    _last_updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transformation logic
CREATE TEMP TABLE stg_seller_performance AS
WITH seller_metrics AS (
    SELECT 
        oi.seller_id,
        SUM(oi.price) as total_revenue,
        COUNT(DISTINCT oi.order_id) as total_orders,
        COUNT(*) as total_items_sold,
        AVG(oi.price) as avg_item_price,
        MIN(o.order_purchase_timestamp) as active_since
    FROM silver.order_items oi
    JOIN silver.orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1
),
seller_reviews AS (
    SELECT 
        oi.seller_id,
        AVG(r.review_score) as avg_review_score
    FROM silver.order_items oi
    JOIN silver.order_reviews r ON oi.order_id = r.order_id
    GROUP BY 1
),
seller_shipping AS (
    SELECT 
        oi.seller_id,
        COUNT(*) FILTER (WHERE o.order_delivered_customer_date > o.order_estimated_delivery_date)::NUMERIC / COUNT(*)::NUMERIC as late_delivery_rate
    FROM silver.order_items oi
    JOIN silver.orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_estimated_delivery_date IS NOT NULL
    GROUP BY 1
)
SELECT 
    s.seller_id,
    s.seller_city,
    s.seller_state,
    COALESCE(m.total_revenue, 0) as total_revenue,
    COALESCE(m.total_orders, 0) as total_orders,
    COALESCE(m.total_items_sold, 0) as total_items_sold,
    COALESCE(m.avg_item_price, 0) as avg_item_price,
    COALESCE(r.avg_review_score, 0) as avg_review_score,
    COALESCE(sh.late_delivery_rate, 0) as late_delivery_rate,
    m.active_since
FROM silver.sellers s
LEFT JOIN seller_metrics m ON s.seller_id = m.seller_id
LEFT JOIN seller_reviews r ON s.seller_id = r.seller_id
LEFT JOIN seller_shipping sh ON s.seller_id = sh.seller_id;

-- Upsert
INSERT INTO gold.mart_seller_performance (
    seller_id, seller_city, seller_state, total_revenue, total_orders,
    total_items_sold, avg_item_price, avg_review_score, late_delivery_rate,
    active_since, _last_updated_at
)
SELECT *, NOW() FROM stg_seller_performance
ON CONFLICT (seller_id) DO UPDATE SET
    total_revenue = EXCLUDED.total_revenue,
    total_orders = EXCLUDED.total_orders,
    total_items_sold = EXCLUDED.total_items_sold,
    avg_review_score = EXCLUDED.avg_review_score,
    late_delivery_rate = EXCLUDED.late_delivery_rate,
    _last_updated_at = NOW();

-- Column Comments
COMMENT ON TABLE gold.mart_seller_performance IS 'Seller performance mart. Use this for ranking sellers, analyzing delivery reliability, and revenue by seller region.';
