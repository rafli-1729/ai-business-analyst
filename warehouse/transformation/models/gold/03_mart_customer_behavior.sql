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
COMMENT ON TABLE gold.mart_customer_behavior IS 'Customer-centric mart for retention, loyalty, and LTV analysis. Grain: One row per unique customer.';
COMMENT ON COLUMN gold.mart_customer_behavior.customer_unique_id IS 'Primary Key. Unique identifier for the buyer (across multiple orders).';
COMMENT ON COLUMN gold.mart_customer_behavior.customer_city IS 'Latest city name of the buyer.';
COMMENT ON COLUMN gold.mart_customer_behavior.customer_state IS 'State abbreviation of the buyer.';
COMMENT ON COLUMN gold.mart_customer_behavior.first_purchase_at IS 'Timestamp of the customer first ever order.';
COMMENT ON COLUMN gold.mart_customer_behavior.latest_purchase_at IS 'Timestamp of the most recent order.';
COMMENT ON COLUMN gold.mart_customer_behavior.total_orders IS 'Count of unique orders placed by this customer.';
COMMENT ON COLUMN gold.mart_customer_behavior.total_items_bought IS 'Total number of individual items purchased across all orders.';
COMMENT ON COLUMN gold.mart_customer_behavior.total_lifetime_value IS 'Total gross amount (price + freight) spent by the customer.';
COMMENT ON COLUMN gold.mart_customer_behavior.avg_order_value IS 'Average gross value per order for this customer.';
COMMENT ON COLUMN gold.mart_customer_behavior.is_repeat_customer IS 'True if the customer has placed more than one order.';
