-- Wide Table: Fact Order Fulfillment
-- Grain: One row per order
-- Purpose: Logistics performance, delivery SLAs, and customer satisfaction analysis.

CREATE UNLOGGED TABLE IF NOT EXISTS gold.fact_order_fulfillment (
    order_id TEXT PRIMARY KEY,
    customer_unique_id TEXT,
    order_status TEXT,
    order_purchase_timestamp TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,
    delivery_days_actual INTEGER,
    delivery_days_estimated INTEGER,
    is_late_delivery BOOLEAN,
    review_score INTEGER,
    _last_updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexing
CREATE INDEX IF NOT EXISTS idx_gold_fulfillment_status ON gold.fact_order_fulfillment(order_status);
CREATE INDEX IF NOT EXISTS idx_gold_fulfillment_review ON gold.fact_order_fulfillment(review_score);

-- Transformation logic
CREATE TEMP TABLE stg_fulfillment AS
WITH review_agg AS (
    SELECT 
        order_id, 
        AVG(review_score)::INTEGER as avg_score 
    FROM silver.order_reviews 
    GROUP BY 1
)
SELECT 
    o.order_id,
    c.customer_unique_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    EXTRACT(DAY FROM (o.order_delivered_customer_date - o.order_purchase_timestamp))::INTEGER AS delivery_days_actual,
    EXTRACT(DAY FROM (o.order_estimated_delivery_date - o.order_purchase_timestamp))::INTEGER AS delivery_days_estimated,
    (o.order_delivered_customer_date > o.order_estimated_delivery_date) AS is_late_delivery,
    r.avg_score as review_score
FROM silver.orders o
JOIN silver.customers c ON o.customer_id = c.customer_id
LEFT JOIN review_agg r ON o.order_id = r.order_id;

-- Upsert
INSERT INTO gold.fact_order_fulfillment (
    order_id, customer_unique_id, order_status, order_purchase_timestamp,
    order_delivered_customer_date, order_estimated_delivery_date,
    delivery_days_actual, delivery_days_estimated, is_late_delivery, 
    review_score, _last_updated_at
)
SELECT *, NOW() FROM stg_fulfillment
ON CONFLICT (order_id) DO UPDATE SET
    order_status = EXCLUDED.order_status,
    order_delivered_customer_date = EXCLUDED.order_delivered_customer_date,
    is_late_delivery = EXCLUDED.is_late_delivery,
    review_score = EXCLUDED.review_score,
    _last_updated_at = NOW();

-- Column Comments
COMMENT ON TABLE gold.fact_order_fulfillment IS 'Wide table for logistics and fulfillment. Use this for delivery times, late flags, and review scores.';
COMMENT ON COLUMN gold.fact_order_fulfillment.delivery_days_actual IS 'Actual days taken from purchase to delivery.';
COMMENT ON COLUMN gold.fact_order_fulfillment.is_late_delivery IS 'Flag indicating if the delivery happened after the estimated date.';
COMMENT ON COLUMN gold.fact_order_fulfillment.review_score IS 'Customer satisfaction rating (1-5).';
