-- =========================================================
-- gold/05_delivery_metrics.sql
-- =========================================================

DROP TABLE IF EXISTS gold.delivery_metrics CASCADE;

CREATE TABLE gold.delivery_metrics AS

SELECT
    DATE(
        order_purchase_timestamp
    ) AS purchase_date,

    AVG(
        EXTRACT(
            DAY FROM (
                order_delivered_customer_date
                -
                order_purchase_timestamp
            )
        )
    ) AS average_delivery_days,

    AVG(
        CASE
            WHEN order_delivered_customer_date >
                 order_estimated_delivery_date
            THEN 1
            ELSE 0
        END
    ) AS late_delivery_rate

FROM silver.orders

WHERE order_status = 'delivered'

GROUP BY 1;

COMMENT ON TABLE gold.delivery_metrics IS
'Daily delivery efficiency and logistics mart.';