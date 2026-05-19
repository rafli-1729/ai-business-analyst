-- Mart: Customer Retention & Behavior
-- Grain: One row per unique customer
-- Purpose: Analyzing customer lifetime value, frequency, and geographic distribution.

CREATE UNLOGGED TABLE IF NOT EXISTS gold.mart_customer_behavior (
    customer_unique_id TEXT PRIMARY KEY,
    customer_city TEXT,
    customer_state TEXT,
    first_purchase_at TIMESTAMP,
    latest_purchase_at TIMESTAMP,
    total_orders INTEGER,
    total_items_bought INTEGER,
    total_lifetime_value NUMERIC,
    avg_order_value NUMERIC,
    is_repeat_customer BOOLEAN,
    _last_updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transformation logic
CREATE TEMP TABLE stg_customer_behavior AS
SELECT 
    c.customer_unique_id,
    MAX(c.customer_city) as customer_city,
    MAX(c.customer_state) as customer_state,
    MIN(o.order_purchase_timestamp) as first_purchase_at,
    MAX(o.order_purchase_timestamp) as latest_purchase_at,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(oi.order_id) as total_items_bought,
    SUM(oi.price + oi.freight_value) as total_lifetime_value,
    AVG(oi.price + oi.freight_value) as avg_order_value,
    (COUNT(DISTINCT o.order_id) > 1) as is_repeat_customer
FROM silver.customers c
JOIN silver.orders o ON c.customer_id = o.customer_id
JOIN silver.order_items oi ON o.order_id = oi.order_id
GROUP BY 1;

-- Upsert
INSERT INTO gold.mart_customer_behavior (
    customer_unique_id, customer_city, customer_state, first_purchase_at, latest_purchase_at,
    total_orders, total_items_bought, total_lifetime_value, avg_order_value,
    is_repeat_customer, _last_updated_at
)
SELECT *, NOW() FROM stg_customer_behavior
ON CONFLICT (customer_unique_id) DO UPDATE SET
    latest_purchase_at = EXCLUDED.latest_purchase_at,
    total_orders = EXCLUDED.total_orders,
    total_lifetime_value = EXCLUDED.total_lifetime_value,
    is_repeat_customer = EXCLUDED.is_repeat_customer,
    _last_updated_at = NOW();

-- Column Comments
COMMENT ON TABLE gold.mart_customer_behavior IS 'Customer-centric mart for retention and LTV analysis. Use this for repeat buyer statistics.';
COMMENT ON COLUMN gold.mart_customer_behavior.customer_city IS 'City name of the buyer.';
COMMENT ON COLUMN gold.mart_customer_behavior.total_lifetime_value IS 'Total amount spent by the customer across all orders including freight.';
COMMENT ON COLUMN gold.mart_customer_behavior.is_repeat_customer IS 'Indicates if the customer has made more than one purchase.';
