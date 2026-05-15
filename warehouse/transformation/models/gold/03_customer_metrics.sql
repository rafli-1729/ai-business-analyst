DROP TABLE IF EXISTS gold.category_sales CASCADE;

CREATE TABLE gold.category_sales AS

SELECT
    DATE_TRUNC(
        'month',
        o.order_purchase_timestamp
    ) AS month,

    COALESCE(
        pct.product_category_name_english,
        p.product_category_name
    ) AS product_category,

    SUM(op.payment_value) AS revenue,

    COUNT(DISTINCT o.order_id) AS total_orders,

    COUNT(*) AS total_items,

    AVG(orv.review_score) AS avg_review_score

FROM silver.orders AS o

JOIN silver.order_items AS oi
    ON o.order_id = oi.order_id

JOIN silver.products AS p
    ON oi.product_id = p.product_id

LEFT JOIN reference.product_category_name_translation AS pct
    ON p.product_category_name =
       pct.product_category_name

JOIN silver.order_payments AS op
    ON o.order_id = op.order_id

LEFT JOIN silver.order_reviews AS orv
    ON o.order_id = orv.order_id

WHERE o.order_status != 'canceled'

GROUP BY 1, 2;

CREATE INDEX idx_gold_category_sales_month
ON gold.category_sales(month);

CREATE INDEX idx_gold_category_sales_category
ON gold.category_sales(product_category);

COMMENT ON TABLE gold.category_sales IS
'Monthly category-level sales performance mart.';