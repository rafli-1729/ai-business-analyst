DROP TABLE IF EXISTS silver.order_payments CASCADE;

CREATE TABLE silver.order_payments AS

SELECT
    NULLIF(
        TRIM(order_id::TEXT),
        ''
    ) AS order_id,

    payment_sequential::INTEGER
        AS payment_sequential,

    LOWER(
        TRIM(payment_type::TEXT)
    ) AS payment_type,

    payment_installments::INTEGER
        AS payment_installments,

    payment_value::NUMERIC
        AS payment_value

FROM bronze.order_payments;

ALTER TABLE silver.order_payments
ADD PRIMARY KEY(
    order_id,
    payment_sequential
);

ALTER TABLE silver.order_payments
ADD CONSTRAINT fk_order_payments_order
FOREIGN KEY(order_id)
REFERENCES silver.orders(order_id);

CREATE INDEX idx_silver_order_payments_type
ON silver.order_payments(payment_type);

CREATE INDEX idx_silver_order_payments_value
ON silver.order_payments(payment_value);

COMMENT ON TABLE silver.order_payments IS
'Cleaned order payment transactional fact table.';

COMMENT ON COLUMN silver.order_payments.payment_type IS
'Normalized customer payment method.';

COMMENT ON COLUMN silver.order_payments.payment_value IS
'Total payment amount including freight.';