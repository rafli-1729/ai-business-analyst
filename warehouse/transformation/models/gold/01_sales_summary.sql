DROP TABLE IF EXISTS gold.sales_summary CASCADE;

CREATE TABLE gold.sales_summary AS

WITH monthly_sales AS (

    SELECT
        DATE_TRUNC(
            'month',
            o.order_purchase_timestamp
        ) AS month,

        SUM(op.payment_value) AS revenue,

        COUNT(DISTINCT o.order_id) AS total_orders,

        COUNT(
            DISTINCT c.customer_unique_id
        ) AS total_customers,

        COUNT(*) AS total_items,

        AVG(op.payment_value) AS avg_order_value,

        AVG(oi.freight_value) AS avg_freight

    FROM silver.orders AS o

    JOIN silver.customers AS c
        ON o.customer_id = c.customer_id

    JOIN silver.order_items AS oi
        ON o.order_id = oi.order_id

    JOIN silver.order_payments AS op
        ON o.order_id = op.order_id

    WHERE o.order_status != 'canceled'

    GROUP BY 1
),

growth AS (

    SELECT
        *,
        LAG(revenue)
            OVER (ORDER BY month)
            AS previous_revenue,

        LAG(total_orders)
            OVER (ORDER BY month)
            AS previous_orders

    FROM monthly_sales
)

SELECT
    month,

    revenue,

    total_orders,

    total_customers,

    total_items,

    avg_order_value,

    avg_freight,

    CASE
        WHEN previous_revenue = 0
        THEN NULL
        ELSE (
            revenue - previous_revenue
        ) / previous_revenue
    END AS revenue_growth_rate,

    CASE
        WHEN previous_orders = 0
        THEN NULL
        ELSE (
            total_orders - previous_orders
        ) / previous_orders
    END AS order_growth_rate

FROM growth;

CREATE INDEX idx_gold_sales_summary_month
ON gold.sales_summary(month);

COMMENT ON TABLE gold.sales_summary IS
'Monthly business sales summary mart.';

COMMENT ON COLUMN gold.sales_summary.revenue IS
'Total payment revenue including freight.';