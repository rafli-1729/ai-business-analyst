-- =========================================================
-- gold/08_geographic_sales.sql
-- =========================================================

DROP TABLE IF EXISTS gold.geographic_sales CASCADE;

CREATE TABLE gold.geographic_sales AS

SELECT
    DATE(
        o.order_purchase_timestamp
    ) AS purchase_date,

    c.customer_state,

    c.customer_city,

    SUM(op.payment_value)
        AS total_revenue,

    COUNT(DISTINCT o.order_id)
        AS total_orders,

    COUNT(
        DISTINCT c.customer_unique_id
    ) AS total_customers

FROM silver.orders AS o

JOIN silver.customers AS c
    ON o.customer_id = c.customer_id

JOIN silver.order_payments AS op
    ON o.order_id = op.order_id

GROUP BY 1, 2, 3;

COMMENT ON TABLE gold.geographic_sales IS
'Daily geographic sales and customer distribution mart.';