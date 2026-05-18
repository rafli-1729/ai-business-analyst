-- Mart: Monthly Performance Trends
-- Grain: One row per Month
-- Purpose: Executive reporting and growth tracking.

CREATE UNLOGGED TABLE IF NOT EXISTS gold.mart_monthly_performance (
    month_start_date DATE PRIMARY KEY,
    total_revenue NUMERIC,
    total_orders INTEGER,
    total_customers INTEGER,
    avg_order_value NUMERIC,
    _last_updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transformation logic
CREATE TEMP TABLE stg_monthly AS
SELECT 
    DATE_TRUNC('month', order_purchase_timestamp)::DATE as month_start_date,
    SUM(price + freight_value) as total_revenue,
    COUNT(DISTINCT order_id) as total_orders,
    COUNT(DISTINCT customer_id) as total_customers,
    AVG(price + freight_value) as avg_order_value
FROM gold.fact_sales_items
GROUP BY 1;

-- Upsert
INSERT INTO gold.mart_monthly_performance (
    month_start_date, total_revenue, total_orders, total_customers, 
    avg_order_value, _last_updated_at
)
SELECT *, NOW() FROM stg_monthly
ON CONFLICT (month_start_date) DO UPDATE SET
    total_revenue = EXCLUDED.total_revenue,
    total_orders = EXCLUDED.total_orders,
    total_customers = EXCLUDED.total_customers,
    _last_updated_at = NOW();

-- Column Comments
COMMENT ON TABLE gold.mart_monthly_performance IS 'High-level monthly trends. Use this for growth analysis and executive summaries.';
COMMENT ON COLUMN gold.mart_monthly_performance.month_start_date IS 'The first day of the month for the reported metrics.';
