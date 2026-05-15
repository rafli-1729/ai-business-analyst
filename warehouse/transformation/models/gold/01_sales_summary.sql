DROP TABLE IF EXISTS gold.sales_summary CASCADE;
CREATE TABLE gold.sales_summary AS

SELECT
    DATE(
        o.order_purchase_timestamp
    ) AS purchase_date,

    SUM(op.payment_value)
        AS total_revenue,

    COUNT(DISTINCT o.order_id)
        AS total_orders,

    COUNT(
        DISTINCT c.customer_unique_id
    ) AS total_customers,

    COUNT(*)
        AS total_items,

    AVG(op.payment_value)
        AS average_order_value,

    AVG(oi.freight_value)
        AS average_freight_value

FROM silver.orders AS o

JOIN silver.customers AS c
    ON o.customer_id = c.customer_id

JOIN silver.order_items AS oi
    ON o.order_id = oi.order_id

JOIN silver.order_payments AS op
    ON o.order_id = op.order_id

WHERE o.order_status != 'canceled'

GROUP BY 1;

CREATE INDEX idx_sales_summary_purchase_date
ON gold.sales_summary(purchase_date);

COMMENT ON TABLE gold.sales_summary IS
'Daily business sales performance summary mart.';

COMMENT ON COLUMN gold.sales_summary.purchase_date IS
'Purchase date at daily grain. Format: YYYY-MM-DD.';

COMMENT ON COLUMN gold.sales_summary.total_revenue IS
'Total successful payment value in Brazilian Real (BRL).';

COMMENT ON COLUMN gold.sales_summary.total_orders IS
'Total distinct orders purchased on the date.';

COMMENT ON COLUMN gold.sales_summary.total_customers IS
'Total unique customers purchasing on the date.';

COMMENT ON COLUMN gold.sales_summary.total_items IS
'Total items sold on the date.';

COMMENT ON COLUMN gold.sales_summary.average_order_value IS
'Average payment value per order in BRL.';

COMMENT ON COLUMN gold.sales_summary.average_freight_value IS
'Average freight cost per order item in BRL.';