DROP TABLE IF EXISTS gold.delivery_metrics CASCADE;

CREATE TABLE gold.delivery_metrics AS

SELECT
    DATE_TRUNC(
        'month',
        order_purchase_timestamp
    ) AS month,

    AVG(
        EXTRACT(
            DAY FROM (
                order_delivered_customer_date
                -
                order_purchase_timestamp
            )
        )
    ) AS avg_delivery_days,

    AVG(
        EXTRACT(
            DAY FROM (
                order_estimated_delivery_date
                -
                order_delivered_customer_date
            )
        )
    ) AS avg_estimated_gap_days,

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

CREATE INDEX idx_gold_delivery_metrics_month
ON gold.delivery_metrics(month);

COMMENT ON TABLE gold.delivery_metrics IS
'Monthly delivery and logistics performance mart.';