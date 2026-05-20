-- Wide Table: Fact Sales Items
SET default_transaction_read_only = off;
-- Grain: One row per order item
-- Purpose: Primary table for revenue, product category, and basic geographic analysis.

CREATE UNLOGGED TABLE IF NOT EXISTS gold.fact_sales_items (
    order_item_key TEXT PRIMARY KEY,
    order_id TEXT,
    order_status TEXT,
    order_purchase_timestamp TIMESTAMP,
    product_id TEXT,
    product_category_name TEXT,
    product_weight_g NUMERIC,
    product_length_cm NUMERIC,
    product_height_cm NUMERIC,
    product_width_cm NUMERIC,
    seller_id TEXT,
    seller_city TEXT,
    seller_state TEXT,
    customer_id TEXT,
    customer_city TEXT,
    customer_state TEXT,
    payment_type TEXT,
    payment_installments INTEGER,
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
CREATE INDEX IF NOT EXISTS idx_gold_fact_sales_cust_city ON gold.fact_sales_items(customer_city);
CREATE INDEX IF NOT EXISTS idx_gold_fact_sales_status ON gold.fact_sales_items(order_status);

-- Transformation logic
CREATE TEMP TABLE stg_fact_sales_items AS
WITH primary_payments AS (
    SELECT 
        order_id,
        payment_type,
        payment_installments,
        ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY payment_value DESC) as rn
    FROM silver.order_payments
)
SELECT 
    (oi.order_id || '-' || oi.order_item_id) AS order_item_key,
    oi.order_id,
    o.order_status,
    o.order_purchase_timestamp,
    oi.product_id,
    p.product_category_name,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,
    oi.seller_id,
    s.seller_city,
    s.seller_state,
    o.customer_id,
    c.customer_city,
    c.customer_state,
    pp.payment_type,
    pp.payment_installments,
    oi.price,
    oi.freight_value,
    (oi.price + oi.freight_value) AS total_value
FROM silver.order_items oi
JOIN silver.orders o ON oi.order_id = o.order_id
LEFT JOIN silver.products p ON oi.product_id = p.product_id
LEFT JOIN silver.sellers s ON oi.seller_id = s.seller_id
LEFT JOIN silver.customers c ON o.customer_id = c.customer_id
LEFT JOIN primary_payments pp ON o.order_id = pp.order_id AND pp.rn = 1;

-- Upsert
INSERT INTO gold.fact_sales_items (
    order_item_key, order_id, order_status, order_purchase_timestamp, 
    product_id, product_category_name, product_weight_g, 
    product_length_cm, product_height_cm, product_width_cm,
    seller_id, seller_city, seller_state, customer_id, customer_city, 
    customer_state, payment_type, payment_installments, price, 
    freight_value, total_value, _last_updated_at
)
SELECT *, NOW() FROM stg_fact_sales_items
ON CONFLICT (order_item_key) DO UPDATE SET
    order_status = EXCLUDED.order_status,
    order_purchase_timestamp = EXCLUDED.order_purchase_timestamp,
    product_category_name = EXCLUDED.product_category_name,
    product_weight_g = EXCLUDED.product_weight_g,
    product_length_cm = EXCLUDED.product_length_cm,
    product_height_cm = EXCLUDED.product_height_cm,
    product_width_cm = EXCLUDED.product_width_cm,
    seller_city = EXCLUDED.seller_city,
    customer_city = EXCLUDED.customer_city,
    payment_type = EXCLUDED.payment_type,
    payment_installments = EXCLUDED.payment_installments,
    price = EXCLUDED.price,
    freight_value = EXCLUDED.freight_value,
    total_value = EXCLUDED.total_value,
    _last_updated_at = NOW();

-- Column Comments for LLM Context
COMMENT ON TABLE gold.fact_sales_items IS 'Ultimate wide table for sales analysis. Use this for revenue, product ranking, and geographic trends. Grain: One row per order item.';
COMMENT ON COLUMN gold.fact_sales_items.order_item_key IS 'Primary Key. Format: order_id-order_item_id.';
COMMENT ON COLUMN gold.fact_sales_items.order_id IS 'Unique identifier for the order.';
COMMENT ON COLUMN gold.fact_sales_items.order_status IS 'Status of the order (delivered, canceled, etc). Filter by delivered for true revenue analysis.';
COMMENT ON COLUMN gold.fact_sales_items.order_purchase_timestamp IS 'Timestamp when the order was placed.';
COMMENT ON COLUMN gold.fact_sales_items.product_id IS 'Unique identifier for the product.';
COMMENT ON COLUMN gold.fact_sales_items.product_category_name IS 'Normalized product category name in English. Format: snake_case (e.g., "health_beauty").';
COMMENT ON COLUMN gold.fact_sales_items.product_weight_g IS 'Weight of the product in grams.';
COMMENT ON COLUMN gold.fact_sales_items.product_length_cm IS 'Length of the product in centimeters.';
COMMENT ON COLUMN gold.fact_sales_items.product_height_cm IS 'Height of the product in centimeters.';
COMMENT ON COLUMN gold.fact_sales_items.product_width_cm IS 'Width of the product in centimeters.';
COMMENT ON COLUMN gold.fact_sales_items.seller_id IS 'Unique identifier for the seller.';
COMMENT ON COLUMN gold.fact_sales_items.seller_city IS 'City where the seller is located. Format: Title Case (e.g., "São Paulo"), UTF-8.';
COMMENT ON COLUMN gold.fact_sales_items.seller_state IS 'State where the seller is located.';
COMMENT ON COLUMN gold.fact_sales_items.customer_id IS 'Link to the specific customer-order record.';
COMMENT ON COLUMN gold.fact_sales_items.customer_city IS 'City where the buyer is located. Format: Title Case (e.g., "Rio de Janeiro"), UTF-8.';
COMMENT ON COLUMN gold.fact_sales_items.customer_state IS 'State where the buyer is located.';
COMMENT ON COLUMN gold.fact_sales_items.payment_type IS 'Method of payment (credit_card, boleto, voucher, debit_card).';
COMMENT ON COLUMN gold.fact_sales_items.payment_installments IS 'Number of installments chosen for the payment.';
COMMENT ON COLUMN gold.fact_sales_items.price IS 'Selling price of the item.';
COMMENT ON COLUMN gold.fact_sales_items.freight_value IS 'Shipping cost for the item.';
COMMENT ON COLUMN gold.fact_sales_items.total_value IS 'Gross transaction value (Price + Freight). Use this for total revenue.';
