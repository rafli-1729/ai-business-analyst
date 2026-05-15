-- =========================================================
-- gold/04_seller_performance.sql
-- =========================================================

DROP TABLE IF EXISTS gold.seller_performance CASCADE;

CREATE TABLE gold.seller_performance AS

SELECT
    s.seller_id,

    s.seller_state,

    COUNT(DISTINCT o.order_id)
        AS total_orders,

    SUM(op.payment_value)
        AS total_revenue,

    AVG(orv.review_score)
        AS average_review_score,

    AVG(
        EXTRACT(
            DAY FROM (
                o.order_delivered_customer_date
                -
                o.order_purchase_timestamp
            )
        )
    ) AS average_delivery_days

FROM silver.sellers AS s

JOIN silver.order_items AS oi
    ON s.seller_id = oi.seller_id

JOIN silver.orders AS o
    ON oi.order_id = o.order_id

JOIN silver.order_payments AS op
    ON o.order_id = op.order_id

LEFT JOIN silver.order_reviews AS orv
    ON o.order_id = orv.order_id

WHERE o.order_status != 'canceled'

GROUP BY 1, 2;

COMMENT ON TABLE gold.seller_performance IS
'Seller-level sales and operational performance mart.';