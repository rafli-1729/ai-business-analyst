DROP TABLE IF EXISTS gold.order_item_facts CASCADE;

CREATE TABLE gold.order_item_facts AS
WITH review_by_order AS (
    SELECT
        rev.order_id,
        AVG(rev.review_score::NUMERIC) AS customer_satisfaction_score,
        COUNT(*) AS review_count,
        MAX(
            CASE
                WHEN rev.review_score <= 2 THEN 1
                ELSE 0
            END
        ) AS has_low_review_score
    FROM silver.order_reviews AS rev
    WHERE rev.is_review_score_valid IS TRUE
    GROUP BY rev.order_id
),
payment_by_order AS (
    SELECT
        pay.order_id,
        COUNT(*) AS payment_count,
        SUM(pay.payment_value) AS total_payment_value,
        MAX(pay.payment_installments) AS installment_count,
        STRING_AGG(DISTINCT pay.payment_type, ', ' ORDER BY pay.payment_type) AS payment_methods,
        COUNT(DISTINCT pay.payment_type) AS payment_method_count,
        MAX(
            CASE
                WHEN pay.payment_installments > 1 THEN 1
                ELSE 0
            END
        ) AS has_installment_payment
    FROM silver.order_payments AS pay
    WHERE pay.is_payment_value_valid IS TRUE
    GROUP BY pay.order_id
),
order_revenue AS (
    SELECT
        item.order_id,
        SUM(item.price) AS order_item_revenue,
        SUM(item.price + item.freight_value) AS order_total_cost,
        SUM(item.freight_value) AS order_shipping_cost,
        COUNT(*) AS order_item_count
    FROM silver.order_items AS item
    WHERE item.is_price_valid IS TRUE
      AND item.is_freight_valid IS TRUE
    GROUP BY item.order_id
),
base_facts AS (
    SELECT
        item.order_id,
        item.order_item_id,
        ord.order_status,
        ord.order_purchase_timestamp,
        ord.order_approved_at,
        ord.order_delivered_carrier_date,
        ord.order_delivered_customer_date,
        ord.order_estimated_delivery_date,
        ord.is_temporal_sequence_valid,
        ord.is_delivered_late,
        cust.customer_id,
        cust.customer_unique_id,
        cust.customer_city,
        cust.customer_state,
        cust_geo.geolocation_lat AS customer_lat,
        cust_geo.geolocation_lng AS customer_lng,
        prod.product_id,
        COALESCE(
            trans.product_category_name_english,
            prod.product_category_name,
            'unknown'
        ) AS product_category_name,
        prod.product_name_length,
        prod.product_description_length,
        prod.product_photos_qty,
        prod.product_weight_g,
        prod.product_length_cm,
        prod.product_height_cm,
        prod.product_width_cm,
        prod.product_volume_cm3,
        prod.product_density_g_per_cm3 AS product_density,
        sell.seller_id,
        sell.seller_city,
        sell.seller_state,
        sell_geo.geolocation_lat AS seller_lat,
        sell_geo.geolocation_lng AS seller_lng,
        item.shipping_limit_date,
        item.price AS order_item_revenue,
        item.freight_value AS order_item_shipping_cost,
        item.price + item.freight_value AS total_order_item_cost,
        orev.order_total_cost,
        orev.order_shipping_cost,
        orev.order_item_count,
        rev.customer_satisfaction_score,
        rev.review_count,
        rev.has_low_review_score,
        pay.payment_count,
        pay.total_payment_value,
        pay.installment_count,
        pay.payment_methods,
        pay.payment_method_count,
        pay.has_installment_payment,
        gold.haversine_km(
            cust_geo.geolocation_lat,
            cust_geo.geolocation_lng,
            sell_geo.geolocation_lat,
            sell_geo.geolocation_lng
        ) AS customer_seller_distance_km
    FROM silver.order_items AS item
    JOIN silver.orders AS ord
      ON ord.order_id = item.order_id
    LEFT JOIN silver.customers AS cust
      ON cust.customer_id = ord.customer_id
    LEFT JOIN silver.geolocation_zip_prefixes AS cust_geo
      ON cust_geo.geolocation_zip_code_prefix = cust.customer_zip_code_prefix
    LEFT JOIN silver.products AS prod
      ON prod.product_id = item.product_id
    LEFT JOIN silver.product_category_name_translation AS trans
      ON trans.product_category_name = prod.product_category_name
    LEFT JOIN silver.sellers AS sell
      ON sell.seller_id = item.seller_id
    LEFT JOIN silver.geolocation_zip_prefixes AS sell_geo
      ON sell_geo.geolocation_zip_code_prefix = sell.seller_zip_code_prefix
    LEFT JOIN review_by_order AS rev
      ON rev.order_id = item.order_id
    LEFT JOIN payment_by_order AS pay
      ON pay.order_id = item.order_id
    LEFT JOIN order_revenue AS orev
      ON orev.order_id = item.order_id
    WHERE item.is_price_valid IS TRUE
      AND item.is_freight_valid IS TRUE
      AND ord.is_customer_fk_valid IS TRUE
),
customer_aggregates AS (
    SELECT
        bf.customer_unique_id,
        COUNT(DISTINCT bf.order_id) AS customer_total_orders,
        SUM(bf.total_order_item_cost) AS customer_total_spent,
        gold.safe_divide(
            SUM(bf.total_order_item_cost),
            COUNT(DISTINCT bf.order_id)::NUMERIC
        ) AS customer_avg_order_value,
        EXTRACT(
            DAY FROM MAX(bf.order_purchase_timestamp) - MIN(bf.order_purchase_timestamp)
        )::NUMERIC AS customer_lifetime_days,
        gold.safe_divide(
            COUNT(DISTINCT bf.order_id)::NUMERIC,
            NULLIF(EXTRACT(DAY FROM MAX(bf.order_purchase_timestamp) - MIN(bf.order_purchase_timestamp))::NUMERIC, 0)
        ) AS customer_order_frequency,
        EXTRACT(
            DAY FROM global_dates.max_purchase_timestamp - MAX(bf.order_purchase_timestamp)
        )::NUMERIC AS customer_recency_days
    FROM base_facts AS bf
    CROSS JOIN (
        SELECT
            MAX(base_facts_for_max.order_purchase_timestamp) AS max_purchase_timestamp
        FROM base_facts AS base_facts_for_max
    ) AS global_dates
    GROUP BY
        bf.customer_unique_id,
        global_dates.max_purchase_timestamp
),
customer_features AS (
    SELECT
        ca.customer_unique_id,
        ca.customer_total_orders,
        ca.customer_total_spent,
        ca.customer_avg_order_value,
        ca.customer_lifetime_days,
        ca.customer_order_frequency,
        ca.customer_recency_days,
        NTILE(5) OVER (
            ORDER BY ca.customer_recency_days DESC NULLS LAST
        ) AS customer_recency_score,
        NTILE(5) OVER (
            ORDER BY ca.customer_total_orders ASC NULLS LAST
        ) AS customer_frequency_score,
        NTILE(5) OVER (
            ORDER BY ca.customer_total_spent ASC NULLS LAST
        ) AS customer_monetary_score
    FROM customer_aggregates AS ca
),
seller_features AS (
    SELECT
        bf.seller_id,
        COUNT(DISTINCT bf.order_id) AS seller_total_orders,
        SUM(bf.order_item_revenue) AS seller_total_revenue,
        COUNT(DISTINCT bf.customer_unique_id) AS seller_unique_customers,
        AVG(bf.customer_satisfaction_score) AS seller_avg_review_score,
        AVG(
            EXTRACT(
                EPOCH FROM (bf.order_delivered_customer_date - bf.order_estimated_delivery_date)
            ) / 86400.0
        ) AS seller_avg_delivery_delay,
        AVG(
            CASE
                WHEN bf.is_delivered_late THEN 1.0
                ELSE 0.0
            END
        ) AS seller_late_delivery_rate,
        DENSE_RANK() OVER (
            ORDER BY SUM(bf.order_item_revenue) DESC NULLS LAST
        ) AS seller_revenue_rank
    FROM base_facts AS bf
    GROUP BY bf.seller_id
),
product_features AS (
    SELECT
        bf.product_id,
        AVG(bf.customer_satisfaction_score) AS product_avg_review,
        AVG(bf.order_item_shipping_cost) AS product_avg_shipping_cost,
        AVG(
            CASE
                WHEN bf.has_low_review_score = 1 OR bf.is_delivered_late THEN 1.0
                ELSE 0.0
            END
        ) AS product_return_risk_proxy
    FROM base_facts AS bf
    GROUP BY bf.product_id
)
SELECT
    bf.order_id,
    bf.order_item_id,
    bf.order_status,
    bf.customer_id,
    bf.customer_unique_id,
    bf.customer_city,
    bf.customer_state,
    bf.customer_lat,
    bf.customer_lng,
    bf.seller_id,
    bf.seller_city,
    bf.seller_state,
    bf.seller_lat,
    bf.seller_lng,
    bf.product_id,
    bf.product_category_name,
    bf.product_name_length,
    bf.product_description_length,
    bf.product_photos_qty,
    bf.product_weight_g,
    bf.product_length_cm,
    bf.product_height_cm,
    bf.product_width_cm,
    bf.product_volume_cm3,
    bf.product_density,
    pf.product_avg_review,
    pf.product_avg_shipping_cost,
    pf.product_return_risk_proxy,
    bf.order_purchase_timestamp,
    bf.order_approved_at,
    bf.shipping_limit_date,
    bf.order_delivered_carrier_date,
    bf.order_delivered_customer_date,
    bf.order_estimated_delivery_date,
    EXTRACT(YEAR FROM bf.order_purchase_timestamp)::INTEGER AS purchase_year,
    EXTRACT(MONTH FROM bf.order_purchase_timestamp)::INTEGER AS purchase_month,
    DATE_TRUNC('month', bf.order_purchase_timestamp)::DATE AS purchase_month_start_date,
    EXTRACT(DAY FROM bf.order_purchase_timestamp)::INTEGER AS purchase_day,
    EXTRACT(ISODOW FROM bf.order_purchase_timestamp)::INTEGER AS purchase_weekday,
    EXTRACT(HOUR FROM bf.order_purchase_timestamp)::INTEGER AS purchase_hour,
    EXTRACT(ISODOW FROM bf.order_purchase_timestamp) IN (6, 7) AS is_weekend,
    TO_CHAR(bf.order_purchase_timestamp, 'MM-DD') IN (
        '01-01',
        '04-21',
        '05-01',
        '09-07',
        '10-12',
        '11-02',
        '11-15',
        '12-25'
    ) AS is_holiday,
    CASE
        WHEN EXTRACT(MONTH FROM bf.order_purchase_timestamp) IN (12, 1, 2) THEN 'summer'
        WHEN EXTRACT(MONTH FROM bf.order_purchase_timestamp) IN (3, 4, 5) THEN 'autumn'
        WHEN EXTRACT(MONTH FROM bf.order_purchase_timestamp) IN (6, 7, 8) THEN 'winter'
        WHEN EXTRACT(MONTH FROM bf.order_purchase_timestamp) IN (9, 10, 11) THEN 'spring'
        ELSE 'unknown'
    END AS purchase_season,
    bf.order_item_revenue,
    bf.order_item_shipping_cost,
    bf.total_order_item_cost,
    bf.order_total_cost,
    bf.order_shipping_cost,
    bf.order_item_count,
    bf.customer_satisfaction_score,
    bf.review_count,
    COALESCE(bf.has_installment_payment, 0) = 1 AS is_installment_payment,
    COALESCE(bf.installment_count, 0) AS installment_count,
    COALESCE(bf.payment_count, 0) AS payment_count,
    COALESCE(bf.payment_method_count, 0) AS payment_method_count,
    bf.payment_methods,
    COALESCE(bf.payment_count, 0) > 1 AS multi_payment_used,
    CASE
        WHEN COALESCE(bf.payment_count, 0) > 1
          OR COALESCE(bf.payment_method_count, 0) > 1
          OR COALESCE(bf.installment_count, 0) > 1
        THEN 'complex'
        ELSE 'simple'
    END AS payment_complexity,
    gold.safe_divide(bf.total_payment_value, bf.order_total_cost) AS payment_value_to_order_ratio,
    bf.customer_seller_distance_km AS delivery_distance_km,
    bf.customer_seller_distance_km,
    EXTRACT(EPOCH FROM (bf.order_delivered_customer_date - bf.order_purchase_timestamp)) / 86400.0 AS delivery_days,
    EXTRACT(EPOCH FROM (bf.order_estimated_delivery_date - bf.order_purchase_timestamp)) / 86400.0 AS estimated_delivery_days,
    EXTRACT(EPOCH FROM (bf.order_delivered_customer_date - bf.order_estimated_delivery_date)) / 86400.0 AS delivery_delay_days,
    EXTRACT(EPOCH FROM (bf.order_delivered_carrier_date - bf.order_approved_at)) / 86400.0 AS shipping_processing_days,
    EXTRACT(EPOCH FROM (bf.order_delivered_customer_date - bf.order_delivered_carrier_date)) / 86400.0 AS carrier_handling_days,
    gold.safe_divide(
        bf.customer_seller_distance_km::NUMERIC,
        (EXTRACT(EPOCH FROM (bf.order_delivered_customer_date - bf.order_purchase_timestamp)) / 86400.0)::NUMERIC
    ) AS delivery_distance_km_per_day,
    gold.safe_divide(
        (EXTRACT(EPOCH FROM (bf.order_estimated_delivery_date - bf.order_purchase_timestamp)) / 86400.0)::NUMERIC,
        NULLIF((EXTRACT(EPOCH FROM (bf.order_delivered_customer_date - bf.order_purchase_timestamp)) / 86400.0)::NUMERIC, 0)
    ) AS delivery_efficiency_score,
    bf.is_delivered_late,
    LOWER(bf.customer_city) = LOWER(bf.seller_city) AS same_city_delivery,
    bf.customer_state = bf.seller_state AS same_state_delivery,
    bf.customer_state <> bf.seller_state AS cross_region_delivery,
    CASE
        WHEN bf.customer_seller_distance_km IS NULL THEN NULL
        WHEN bf.customer_seller_distance_km <= 50 THEN 'urban'
        WHEN bf.customer_seller_distance_km <= 300 THEN 'regional'
        ELSE 'long_distance'
    END AS urban_delivery_proxy,
    CASE
        WHEN bf.customer_seller_distance_km IS NULL THEN NULL
        WHEN bf.customer_seller_distance_km > 1000 THEN 'high'
        WHEN bf.customer_seller_distance_km > 300 OR bf.customer_state <> bf.seller_state THEN 'medium'
        ELSE 'low'
    END AS regional_delivery_difficulty,
    cf.customer_total_orders,
    cf.customer_total_spent,
    cf.customer_avg_order_value,
    cf.customer_lifetime_days,
    cf.customer_order_frequency,
    cf.customer_recency_days,
    cf.customer_recency_score,
    cf.customer_frequency_score,
    cf.customer_monetary_score,
    cf.customer_recency_score + cf.customer_frequency_score + cf.customer_monetary_score AS customer_rfm_score,
    sf.seller_total_orders,
    sf.seller_total_revenue,
    sf.seller_unique_customers,
    sf.seller_avg_review_score,
    sf.seller_avg_delivery_delay,
    sf.seller_late_delivery_rate,
    sf.seller_revenue_rank,
    bf.is_temporal_sequence_valid
FROM base_facts AS bf
LEFT JOIN customer_features AS cf
  ON cf.customer_unique_id = bf.customer_unique_id
LEFT JOIN seller_features AS sf
  ON sf.seller_id = bf.seller_id
LEFT JOIN product_features AS pf
  ON pf.product_id = bf.product_id;

CREATE INDEX IF NOT EXISTS idx_gold_order_item_facts_order_id
    ON gold.order_item_facts (order_id);
CREATE INDEX IF NOT EXISTS idx_gold_order_item_facts_customer_unique_id
    ON gold.order_item_facts (customer_unique_id);
CREATE INDEX IF NOT EXISTS idx_gold_order_item_facts_seller_id
    ON gold.order_item_facts (seller_id);
CREATE INDEX IF NOT EXISTS idx_gold_order_item_facts_product_id
    ON gold.order_item_facts (product_id);
CREATE INDEX IF NOT EXISTS idx_gold_order_item_facts_category
    ON gold.order_item_facts (product_category_name);
CREATE INDEX IF NOT EXISTS idx_gold_order_item_facts_purchase_month
    ON gold.order_item_facts (purchase_month_start_date);
CREATE INDEX IF NOT EXISTS idx_gold_order_item_facts_customer_state
    ON gold.order_item_facts (customer_state);
CREATE INDEX IF NOT EXISTS idx_gold_order_item_facts_seller_rank
    ON gold.order_item_facts (seller_revenue_rank);
CREATE INDEX IF NOT EXISTS idx_gold_order_item_facts_revenue
    ON gold.order_item_facts (order_item_revenue DESC);
