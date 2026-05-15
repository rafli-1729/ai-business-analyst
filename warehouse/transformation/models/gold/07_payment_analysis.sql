-- =========================================================
-- gold/07_payment_analysis.sql
-- =========================================================

DROP TABLE IF EXISTS gold.payment_analysis CASCADE;

CREATE TABLE gold.payment_analysis AS

SELECT
    DATE(
        o.order_purchase_timestamp
    ) AS purchase_date,

    op.payment_type,

    COUNT(*) AS total_payments,

    SUM(op.payment_value)
        AS total_payment_value,

    AVG(op.payment_installments)
        AS average_installments

FROM silver.order_payments AS op

JOIN silver.orders AS o
    ON op.order_id = o.order_id

GROUP BY 1, 2;

COMMENT ON TABLE gold.payment_analysis IS
'Daily payment behavior and payment method mart.';