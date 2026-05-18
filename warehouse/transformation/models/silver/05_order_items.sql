-- Silver Order Items: Cleaned & Incremental Upsert
CREATE UNLOGGED TABLE IF NOT EXISTS silver.order_items (
    order_id TEXT,
    order_item_id INTEGER,
    product_id TEXT,
    seller_id TEXT,
    shipping_limit_date TIMESTAMP,
    price NUMERIC,
    freight_value NUMERIC,
    _last_updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (order_id, order_item_id)
);

CREATE TEMP TABLE stg_order_items_cleaned AS
SELECT
    NULLIF(TRIM(order_id::TEXT), '') AS order_id,
    NULLIF(TRIM(order_item_id::TEXT), '')::NUMERIC::INTEGER AS order_item_id,
    NULLIF(TRIM(product_id::TEXT), '') AS product_id,
    NULLIF(TRIM(seller_id::TEXT), '') AS seller_id,
    NULLIF(TRIM(shipping_limit_date::TEXT), '')::TIMESTAMP AS shipping_limit_date,
    NULLIF(TRIM(price::TEXT), '')::NUMERIC AS price,
    NULLIF(TRIM(freight_value::TEXT), '')::NUMERIC AS freight_value
FROM bronze.order_items;

INSERT INTO silver.order_items (
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value,
    _last_updated_at
)
SELECT 
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value,
    NOW()
FROM stg_order_items_cleaned
ON CONFLICT (order_id, order_item_id) 
DO UPDATE SET
    product_id = EXCLUDED.product_id,
    seller_id = EXCLUDED.seller_id,
    shipping_limit_date = EXCLUDED.shipping_limit_date,
    price = EXCLUDED.price,
    freight_value = EXCLUDED.freight_value,
    _last_updated_at = NOW();

CREATE INDEX IF NOT EXISTS idx_silver_order_items_product ON silver.order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_silver_order_items_seller ON silver.order_items(seller_id);

COMMENT ON TABLE silver.order_items IS 'Cleaned order item level transactional fact table.';
