-- Silver Orders: Cleaned & Incremental Upsert
CREATE UNLOGGED TABLE IF NOT EXISTS silver.orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    order_status TEXT,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,
    _last_updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TEMP TABLE stg_orders_cleaned AS
SELECT
    NULLIF(TRIM(order_id::TEXT), '') AS order_id,
    NULLIF(TRIM(customer_id::TEXT), '') AS customer_id,
    LOWER(TRIM(order_status::TEXT)) AS order_status,
    NULLIF(TRIM(order_purchase_timestamp::TEXT), '')::TIMESTAMP AS order_purchase_timestamp,
    NULLIF(TRIM(order_approved_at::TEXT), '')::TIMESTAMP AS order_approved_at,
    NULLIF(TRIM(order_delivered_carrier_date::TEXT), '')::TIMESTAMP AS order_delivered_carrier_date,
    NULLIF(TRIM(order_delivered_customer_date::TEXT), '')::TIMESTAMP AS order_delivered_customer_date,
    NULLIF(TRIM(order_estimated_delivery_date::TEXT), '')::TIMESTAMP AS order_estimated_delivery_date
FROM bronze.orders;

INSERT INTO silver.orders (
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    _last_updated_at
)
SELECT 
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    NOW()
FROM stg_orders_cleaned
ON CONFLICT (order_id) 
DO UPDATE SET
    customer_id = EXCLUDED.customer_id,
    order_status = EXCLUDED.order_status,
    order_purchase_timestamp = EXCLUDED.order_purchase_timestamp,
    order_approved_at = EXCLUDED.order_approved_at,
    order_delivered_carrier_date = EXCLUDED.order_delivered_carrier_date,
    order_delivered_customer_date = EXCLUDED.order_delivered_customer_date,
    order_estimated_delivery_date = EXCLUDED.order_estimated_delivery_date,
    _last_updated_at = NOW();

CREATE INDEX IF NOT EXISTS idx_silver_orders_customer_id ON silver.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_silver_orders_purchase_timestamp ON silver.orders(order_purchase_timestamp);
CREATE INDEX IF NOT EXISTS idx_silver_orders_status ON silver.orders(order_status);

COMMENT ON TABLE silver.orders IS 'Cleaned transactional orders fact table.';
