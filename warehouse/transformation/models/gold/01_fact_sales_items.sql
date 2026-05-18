-- Wide Table: Fact Sales Items
SET default_transaction_read_only = off;
-- Grain: One row per order item
-- Purpose: Primary table for revenue, product category, and basic geographic analysis.

CREATE UNLOGGED TABLE IF NOT EXISTS gold.fact_sales_items (
    order_item_key TEXT PRIMARY KEY,
    order_id TEXT,
    order_purchase_timestamp TIMESTAMP,
    product_id TEXT,
    product_category_name TEXT,
    seller_id TEXT,
    seller_state TEXT,
    customer_id TEXT,
    customer_state TEXT,
    price NUMERIC,
    freight_value NUMERIC,
    total_value NUMERIC,
    _last_updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexing for LLM performance
CREATE INDEX IF NOT EXISTS idx_gold_fact_sales_order_id ON gold.fact_sales_items(order_id);
CREATE INDEX IF NOT EXISTS idx_gold_fact_sales_timestamp ON gold.fact_sales_items(order_purchase_timestamp);
CREATE INDEX IF NOT EXISTS idx_gold_fact_sales_category ON gold.fact_sales_items(product_category_name);
CREATE INDEX IF NOT EXISTS idx_gold_fact_sales_cust_state ON gold.fact_sales_items(customer_state);

-- Transformation logic
CREATE TEMP TABLE stg_fact_sales_items AS
SELECT 
    (oi.order_id || '-' || oi.order_item_id) AS order_item_key,
    oi.order_id,
    o.order_purchase_timestamp,
    oi.product_id,
    p.product_category_name,
    oi.seller_id,
    s.seller_state,
    o.customer_id,
    c.customer_state,
    oi.price,
    oi.freight_value,
    (oi.price + oi.freight_value) AS total_value
FROM silver.order_items oi
JOIN silver.orders o ON oi.order_id = o.order_id
LEFT JOIN silver.products p ON oi.product_id = p.product_id
LEFT JOIN silver.sellers s ON oi.seller_id = s.seller_id
LEFT JOIN silver.customers c ON o.customer_id = c.customer_id;

-- Upsert
INSERT INTO gold.fact_sales_items (
    order_item_key, order_id, order_purchase_timestamp, product_id, 
    product_category_name, seller_id, seller_state, customer_id, 
    customer_state, price, freight_value, total_value, _last_updated_at
)
SELECT *, NOW() FROM stg_fact_sales_items
ON CONFLICT (order_item_key) DO UPDATE SET
    order_purchase_timestamp = EXCLUDED.order_purchase_timestamp,
    product_category_name = EXCLUDED.product_category_name,
    price = EXCLUDED.price,
    freight_value = EXCLUDED.freight_value,
    total_value = EXCLUDED.total_value,
    _last_updated_at = NOW();

-- Column Comments for LLM Context
COMMENT ON TABLE gold.fact_sales_items IS 'Ultimate wide table for sales analysis. Use this for revenue, product ranking, and geographic trends.';
COMMENT ON COLUMN gold.fact_sales_items.order_item_key IS 'Unique identifier for each item in an order.';
COMMENT ON COLUMN gold.fact_sales_items.product_category_name IS 'Normalized product category name in English.';
COMMENT ON COLUMN gold.fact_sales_items.price IS 'Selling price of the product item.';
COMMENT ON COLUMN gold.fact_sales_items.freight_value IS 'Shipping cost for the product item.';
COMMENT ON COLUMN gold.fact_sales_items.total_value IS 'Gross value (Price + Freight). Use this for total revenue calculations.';
COMMENT ON COLUMN gold.fact_sales_items.customer_state IS 'Two-letter Brazilian state code of the buyer.';
