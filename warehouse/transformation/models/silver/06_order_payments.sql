-- Silver Order Payments: Cleaned & Incremental Upsert
CREATE UNLOGGED TABLE IF NOT EXISTS silver.order_payments (
    order_id TEXT,
    payment_sequential INTEGER,
    payment_type TEXT,
    payment_installments INTEGER,
    payment_value NUMERIC,
    _last_updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (order_id, payment_sequential)
);

CREATE TEMP TABLE stg_order_payments_cleaned AS
SELECT
    NULLIF(TRIM(order_id::TEXT), '') AS order_id,
    NULLIF(TRIM(payment_sequential::TEXT), '')::NUMERIC::INTEGER AS payment_sequential,
    LOWER(TRIM(payment_type::TEXT)) AS payment_type,
    NULLIF(TRIM(payment_installments::TEXT), '')::NUMERIC::INTEGER AS payment_installments,
    NULLIF(TRIM(payment_value::TEXT), '')::NUMERIC AS payment_value
FROM bronze.order_payments;

INSERT INTO silver.order_payments (
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value,
    _last_updated_at
)
SELECT 
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value,
    NOW()
FROM stg_order_payments_cleaned
ON CONFLICT (order_id, payment_sequential) 
DO UPDATE SET
    payment_type = EXCLUDED.payment_type,
    payment_installments = EXCLUDED.payment_installments,
    payment_value = EXCLUDED.payment_value,
    _last_updated_at = NOW();

CREATE INDEX IF NOT EXISTS idx_silver_order_payments_type ON silver.order_payments(payment_type);
CREATE INDEX IF NOT EXISTS idx_silver_order_payments_value ON silver.order_payments(payment_value);

COMMENT ON TABLE silver.order_payments IS 'Cleaned order payment transactional fact table.';
