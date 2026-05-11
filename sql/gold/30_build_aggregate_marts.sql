DROP TABLE IF EXISTS gold.delivery_performance CASCADE;
DROP TABLE IF EXISTS gold.payment_method_performance CASCADE;
DROP TABLE IF EXISTS gold.seller_performance CASCADE;
DROP TABLE IF EXISTS gold.state_performance CASCADE;
DROP TABLE IF EXISTS gold.category_performance CASCADE;
DROP TABLE IF EXISTS gold.monthly_revenue CASCADE;

CREATE TABLE gold.monthly_revenue AS
SELECT
    fact.purchase_month_start_date,
    fact.purchase_year,
    fact.purchase_month,
    COUNT(DISTINCT fact.order_id) AS total_orders,
    COUNT(*) AS total_order_items,
    COUNT(DISTINCT fact.customer_unique_id) AS unique_customers,
    SUM(fact.order_item_revenue) AS total_revenue,
    SUM(fact.order_item_shipping_cost) AS total_shipping_revenue,
    SUM(fact.total_order_item_cost) AS total_order_item_cost,
    AVG(fact.customer_satisfaction_score) AS customer_satisfaction_score,
    AVG(fact.delivery_days) AS average_delivery_days,
    AVG(fact.delivery_delay_days) AS average_delivery_delay_days
FROM gold.order_item_facts AS fact
WHERE fact.purchase_month_start_date IS NOT NULL
  AND fact.order_status NOT IN ('canceled', 'unavailable')
GROUP BY
    fact.purchase_month_start_date,
    fact.purchase_year,
    fact.purchase_month;

CREATE TABLE gold.category_performance AS
SELECT
    fact.product_category_name,
    COUNT(DISTINCT fact.order_id) AS total_orders,
    COUNT(*) AS total_order_items,
    COUNT(DISTINCT fact.customer_unique_id) AS unique_customers,
    SUM(fact.order_item_revenue) AS total_revenue,
    SUM(fact.total_order_item_cost) AS total_order_item_cost,
    AVG(fact.customer_satisfaction_score) AS customer_satisfaction_score,
    AVG(fact.product_return_risk_proxy) AS product_return_risk_proxy,
    AVG(fact.product_avg_shipping_cost) AS average_shipping_cost
FROM gold.order_item_facts AS fact
WHERE fact.order_status NOT IN ('canceled', 'unavailable')
GROUP BY fact.product_category_name;

CREATE TABLE gold.state_performance AS
SELECT
    fact.customer_state,
    COUNT(DISTINCT fact.order_id) AS total_orders,
    COUNT(DISTINCT fact.customer_unique_id) AS unique_customers,
    SUM(fact.order_item_revenue) AS total_revenue,
    SUM(fact.total_order_item_cost) AS total_order_item_cost,
    AVG(fact.customer_satisfaction_score) AS customer_satisfaction_score,
    AVG(fact.delivery_days) AS average_delivery_days,
    AVG(fact.delivery_delay_days) AS average_delivery_delay_days,
    AVG(CASE WHEN fact.is_delivered_late THEN 1.0 ELSE 0.0 END) AS late_delivery_rate
FROM gold.order_item_facts AS fact
WHERE fact.order_status NOT IN ('canceled', 'unavailable')
GROUP BY fact.customer_state;

CREATE TABLE gold.seller_performance AS
SELECT
    fact.seller_id,
    fact.seller_city,
    fact.seller_state,
    MAX(fact.seller_revenue_rank) AS seller_revenue_rank,
    COUNT(DISTINCT fact.order_id) AS total_orders,
    COUNT(*) AS total_order_items,
    COUNT(DISTINCT fact.customer_unique_id) AS unique_customers,
    SUM(fact.order_item_revenue) AS total_revenue,
    AVG(fact.customer_satisfaction_score) AS customer_satisfaction_score,
    AVG(fact.delivery_delay_days) AS average_delivery_delay_days,
    AVG(CASE WHEN fact.is_delivered_late THEN 1.0 ELSE 0.0 END) AS late_delivery_rate
FROM gold.order_item_facts AS fact
WHERE fact.order_status NOT IN ('canceled', 'unavailable')
GROUP BY
    fact.seller_id,
    fact.seller_city,
    fact.seller_state;

CREATE TABLE gold.payment_method_performance AS
SELECT
    fact.payment_methods,
    fact.payment_complexity,
    COUNT(DISTINCT fact.order_id) AS total_orders,
    COUNT(*) AS total_order_items,
    SUM(fact.total_order_item_cost) AS total_order_item_cost,
    AVG(fact.payment_value_to_order_ratio) AS average_payment_value_to_order_ratio,
    AVG(fact.installment_count) AS average_installment_count
FROM gold.order_item_facts AS fact
WHERE fact.order_status NOT IN ('canceled', 'unavailable')
GROUP BY
    fact.payment_methods,
    fact.payment_complexity;

CREATE TABLE gold.delivery_performance AS
SELECT
    fact.purchase_month_start_date,
    fact.customer_state,
    fact.regional_delivery_difficulty,
    COUNT(DISTINCT fact.order_id) AS total_orders,
    COUNT(*) AS total_order_items,
    AVG(fact.delivery_distance_km) AS average_delivery_distance_km,
    AVG(fact.delivery_days) AS average_delivery_days,
    AVG(fact.estimated_delivery_days) AS average_estimated_delivery_days,
    AVG(fact.delivery_delay_days) AS average_delivery_delay_days,
    AVG(fact.delivery_efficiency_score) AS average_delivery_efficiency_score,
    AVG(CASE WHEN fact.is_delivered_late THEN 1.0 ELSE 0.0 END) AS late_delivery_rate,
    AVG(CASE WHEN fact.same_city_delivery THEN 1.0 ELSE 0.0 END) AS same_city_delivery_rate,
    AVG(CASE WHEN fact.same_state_delivery THEN 1.0 ELSE 0.0 END) AS same_state_delivery_rate
FROM gold.order_item_facts AS fact
WHERE fact.order_status NOT IN ('canceled', 'unavailable')
  AND fact.is_temporal_sequence_valid IS TRUE
GROUP BY
    fact.purchase_month_start_date,
    fact.customer_state,
    fact.regional_delivery_difficulty;

CREATE INDEX IF NOT EXISTS idx_gold_monthly_revenue_month
    ON gold.monthly_revenue (purchase_month_start_date);
CREATE INDEX IF NOT EXISTS idx_gold_category_performance_revenue
    ON gold.category_performance (total_revenue DESC);
CREATE INDEX IF NOT EXISTS idx_gold_state_performance_revenue
    ON gold.state_performance (total_revenue DESC);
CREATE INDEX IF NOT EXISTS idx_gold_seller_performance_rank
    ON gold.seller_performance (seller_revenue_rank);
CREATE INDEX IF NOT EXISTS idx_gold_delivery_performance_month_state
    ON gold.delivery_performance (purchase_month_start_date, customer_state);
