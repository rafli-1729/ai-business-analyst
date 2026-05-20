-- Wide Table: Fact Order Fulfillment
-- Grain: One row per order
-- Purpose: Logistics performance, delivery SLAs, and customer satisfaction analysis.

CREATE UNLOGGED TABLE IF NOT EXISTS gold.fact_order_fulfillment (
    order_id TEXT PRIMARY KEY,
    customer_unique_id TEXT,
    customer_city TEXT,
    customer_state TEXT,
    seller_id TEXT,
    seller_city TEXT,
    seller_state TEXT,
    order_status TEXT,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,
    delivery_days_actual INTEGER,
    delivery_days_estimated INTEGER,
    processing_days INTEGER,
    is_late_delivery BOOLEAN,
    review_score INTEGER,
    _last_updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexing
CREATE INDEX IF NOT EXISTS idx_gold_fulfillment_status ON gold.fact_order_fulfillment(order_status);
CREATE INDEX IF NOT EXISTS idx_gold_fulfillment_review ON gold.fact_order_fulfillment(review_score);
CREATE INDEX IF NOT EXISTS idx_gold_fulfillment_cust_city ON gold.fact_order_fulfillment(customer_city);
CREATE INDEX IF NOT EXISTS idx_gold_fulfillment_seller_id ON gold.fact_order_fulfillment(seller_id);

-- Transformation logic
CREATE TEMP TABLE stg_fulfillment AS
WITH review_agg AS (
    SELECT 
        order_id, 
        AVG(review_score)::INTEGER as avg_score 
    FROM silver.order_reviews 
    GROUP BY 1
),
seller_agg AS (
    SELECT 
        oi.order_id,
        oi.seller_id,
        s.seller_city,
        s.seller_state,
        ROW_NUMBER() OVER (PARTITION BY oi.order_id ORDER BY oi.price DESC) as rn
    FROM silver.order_items oi
    JOIN silver.sellers s ON oi.seller_id = s.seller_id
)
SELECT 
    o.order_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    sa.seller_id,
    sa.seller_city,
    sa.seller_state,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    EXTRACT(DAY FROM (o.order_delivered_customer_date - o.order_purchase_timestamp))::INTEGER AS delivery_days_actual,
    EXTRACT(DAY FROM (o.order_estimated_delivery_date - o.order_purchase_timestamp))::INTEGER AS delivery_days_estimated,
    EXTRACT(DAY FROM (o.order_delivered_carrier_date - o.order_approved_at))::INTEGER AS processing_days,
    (o.order_delivered_customer_date > o.order_estimated_delivery_date) AS is_late_delivery,
    r.avg_score as review_score
FROM silver.orders o
JOIN silver.customers c ON o.customer_id = c.customer_id
LEFT JOIN review_agg r ON o.order_id = r.order_id
LEFT JOIN seller_agg sa ON o.order_id = sa.order_id AND sa.rn = 1;

-- Upsert
INSERT INTO gold.fact_order_fulfillment (
    order_id, customer_unique_id, customer_city, customer_state,
    seller_id, seller_city, seller_state, order_status, 
    order_purchase_timestamp, order_approved_at, order_delivered_carrier_date,
    order_delivered_customer_date, order_estimated_delivery_date,
    delivery_days_actual, delivery_days_estimated, processing_days,
    is_late_delivery, review_score, _last_updated_at
)
SELECT *, NOW() FROM stg_fulfillment
ON CONFLICT (order_id) DO UPDATE SET
    order_status = EXCLUDED.order_status,
    order_delivered_customer_date = EXCLUDED.order_delivered_customer_date,
    is_late_delivery = EXCLUDED.is_late_delivery,
    review_score = EXCLUDED.review_score,
    _last_updated_at = NOW();

-- Column Comments
COMMENT ON TABLE gold.fact_order_fulfillment IS 'Wide table for logistics and fulfillment performance. Use this for delivery times, late flags, and review scores. Grain: One row per order.';
COMMENT ON COLUMN gold.fact_order_fulfillment.order_id IS 'Primary Key. Unique identifier for the order.';
COMMENT ON COLUMN gold.fact_order_fulfillment.customer_unique_id IS 'Unique identifier for the buyer (static across multiple orders).';
COMMENT ON COLUMN gold.fact_order_fulfillment.customer_city IS 'City name of the buyer.';
COMMENT ON COLUMN gold.fact_order_fulfillment.customer_state IS 'State abbreviation of the buyer.';
COMMENT ON COLUMN gold.fact_order_fulfillment.seller_id IS 'Unique identifier for the primary seller (highest price item).';
COMMENT ON COLUMN gold.fact_order_fulfillment.seller_city IS 'City name where the seller is located.';
COMMENT ON COLUMN gold.fact_order_fulfillment.seller_state IS 'State abbreviation where the seller is located.';
COMMENT ON COLUMN gold.fact_order_fulfillment.order_status IS 'Status of the order (delivered, canceled, etc).';
COMMENT ON COLUMN gold.fact_order_fulfillment.order_purchase_timestamp IS 'Timestamp when the order was placed.';
COMMENT ON COLUMN gold.fact_order_fulfillment.order_approved_at IS 'Timestamp when payment was approved.';
COMMENT ON COLUMN gold.fact_order_fulfillment.order_delivered_carrier_date IS 'Timestamp when the order was handed to the logistics partner.';
COMMENT ON COLUMN gold.fact_order_fulfillment.order_delivered_customer_date IS 'Actual timestamp when the customer received the order.';
COMMENT ON COLUMN gold.fact_order_fulfillment.order_estimated_delivery_date IS 'The delivery date promised to the customer at purchase.';
COMMENT ON COLUMN gold.fact_order_fulfillment.delivery_days_actual IS 'Actual days taken from purchase to delivery.';
COMMENT ON COLUMN gold.fact_order_fulfillment.delivery_days_estimated IS 'Expected days for delivery estimated at purchase.';
COMMENT ON COLUMN gold.fact_order_fulfillment.processing_days IS 'Days taken from order approval to carrier pickup.';
COMMENT ON COLUMN gold.fact_order_fulfillment.is_late_delivery IS 'Boolean flag. True if order_delivered_customer_date > order_estimated_delivery_date.';
COMMENT ON COLUMN gold.fact_order_fulfillment.review_score IS 'Customer satisfaction rating (1-5).';
