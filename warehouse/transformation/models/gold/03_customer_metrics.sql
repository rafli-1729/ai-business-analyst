-- =========================================================
-- gold/03_customer_metrics.sql
-- =========================================================

DROP TABLE IF EXISTS gold.customer_metrics CASCADE;

CREATE TABLE gold.customer_metrics AS

SELECT
    c.customer_unique_id,

    c.customer_state,

    COUNT(DISTINCT o.order_id)
        AS total_orders,

    SUM(op.payment_value)
        AS total_revenue,

    AVG(op.payment_value)
        AS average_order_value,

    MIN(
        o.order_purchase_timestamp
    ) AS first_purchase_timestamp,

    MAX(
        o.order_purchase_timestamp
    ) AS latest_purchase_timestamp

FROM silver.customers AS c

JOIN silver.orders AS o
    ON c.customer_id = o.customer_id

JOIN silver.order_payments AS op
    ON o.order_id = op.order_id

WHERE o.order_status != 'canceled'

GROUP BY 1, 2;

CREATE INDEX idx_customer_metrics_customer
ON gold.customer_metrics(customer_unique_id);

COMMENT ON TABLE gold.customer_metrics IS
'Customer-level purchasing and revenue behavior mart.';