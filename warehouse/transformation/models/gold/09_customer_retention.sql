-- =========================================================
-- gold/09_customer_retention.sql
-- =========================================================

DROP TABLE IF EXISTS gold.customer_retention CASCADE;

CREATE TABLE gold.customer_retention AS

WITH customer_orders AS (

    SELECT
        c.customer_unique_id,

        COUNT(DISTINCT o.order_id)
            AS total_orders

    FROM silver.customers AS c

    JOIN silver.orders AS o
        ON c.customer_id = o.customer_id

    GROUP BY 1
)

SELECT
    customer_unique_id,

    total_orders,

    CASE
        WHEN total_orders > 1
        THEN TRUE
        ELSE FALSE
    END AS is_repeat_customer

FROM customer_orders;

COMMENT ON TABLE gold.customer_retention IS
'Customer repeat purchase and retention mart.';