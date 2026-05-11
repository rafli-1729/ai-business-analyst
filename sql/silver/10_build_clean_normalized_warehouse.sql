DROP TABLE IF EXISTS silver.data_quality_issues CASCADE;
DROP TABLE IF EXISTS silver.order_payments CASCADE;
DROP TABLE IF EXISTS silver.order_reviews CASCADE;
DROP TABLE IF EXISTS silver.order_items CASCADE;
DROP TABLE IF EXISTS silver.orders CASCADE;
DROP TABLE IF EXISTS silver.products CASCADE;
DROP TABLE IF EXISTS silver.sellers CASCADE;
DROP TABLE IF EXISTS silver.customers CASCADE;
DROP TABLE IF EXISTS silver.geolocation_zip_prefixes CASCADE;
DROP TABLE IF EXISTS silver.product_category_name_translation CASCADE;

CREATE TABLE silver.customers AS
WITH typed_customers AS (
    SELECT
        NULLIF(TRIM(src.customer_id::TEXT), '') AS customer_id,
        NULLIF(TRIM(src.customer_unique_id::TEXT), '') AS customer_unique_id,
        silver.blank_nan_to_null(src.customer_zip_code_prefix::TEXT)::NUMERIC::INTEGER AS customer_zip_code_prefix,
        LOWER(TRIM(REGEXP_REPLACE(src.customer_city::TEXT, '\s+', ' ', 'g'))) AS customer_city,
        UPPER(TRIM(src.customer_state::TEXT)) AS customer_state
    FROM raw.customers AS src
),
deduped_customers AS (
    SELECT
        tc.customer_id,
        tc.customer_unique_id,
        tc.customer_zip_code_prefix,
        tc.customer_city,
        tc.customer_state,
        ROW_NUMBER() OVER (
            PARTITION BY tc.customer_id
            ORDER BY tc.customer_unique_id, tc.customer_zip_code_prefix
        ) AS row_rank
    FROM typed_customers AS tc
)
SELECT
    dc.customer_id,
    dc.customer_unique_id,
    dc.customer_zip_code_prefix,
    dc.customer_city,
    dc.customer_state
FROM deduped_customers AS dc
WHERE dc.row_rank = 1;

CREATE TABLE silver.geolocation_zip_prefixes AS
WITH typed_geolocation AS (
    SELECT
        silver.blank_nan_to_null(src.geolocation_zip_code_prefix::TEXT)::NUMERIC::INTEGER AS geolocation_zip_code_prefix,
        silver.blank_nan_to_null(src.geolocation_lat::TEXT)::DOUBLE PRECISION AS geolocation_lat,
        silver.blank_nan_to_null(src.geolocation_lng::TEXT)::DOUBLE PRECISION AS geolocation_lng,
        LOWER(TRIM(REGEXP_REPLACE(src.geolocation_city::TEXT, '\s+', ' ', 'g'))) AS geolocation_city,
        UPPER(TRIM(src.geolocation_state::TEXT)) AS geolocation_state
    FROM raw.geolocation AS src
),
aggregated_geolocation AS (
    SELECT
        tg.geolocation_zip_code_prefix,
        tg.geolocation_city,
        tg.geolocation_state,
        AVG(tg.geolocation_lat) AS geolocation_lat,
        AVG(tg.geolocation_lng) AS geolocation_lng,
        COUNT(*) AS raw_location_count
    FROM typed_geolocation AS tg
    WHERE tg.geolocation_zip_code_prefix IS NOT NULL
    GROUP BY
        tg.geolocation_zip_code_prefix,
        tg.geolocation_city,
        tg.geolocation_state
),
ranked_geolocation AS (
    SELECT
        ag.geolocation_zip_code_prefix,
        ag.geolocation_lat,
        ag.geolocation_lng,
        ag.geolocation_city,
        ag.geolocation_state,
        ag.raw_location_count,
        ROW_NUMBER() OVER (
            PARTITION BY ag.geolocation_zip_code_prefix
            ORDER BY
                ag.raw_location_count DESC,
                ag.geolocation_state,
                ag.geolocation_city
        ) AS row_rank
    FROM aggregated_geolocation AS ag
)
SELECT
    rg.geolocation_zip_code_prefix,
    rg.geolocation_lat,
    rg.geolocation_lng,
    rg.geolocation_city,
    rg.geolocation_state,
    rg.raw_location_count
FROM ranked_geolocation AS rg
WHERE rg.row_rank = 1;

CREATE TABLE silver.products AS
WITH typed_products AS (
    SELECT
        NULLIF(TRIM(src.product_id::TEXT), '') AS product_id,
        NULLIF(LOWER(TRIM(src.product_category_name::TEXT)), '') AS product_category_name,
        silver.blank_nan_to_null(src.product_name_lenght::TEXT)::NUMERIC::INTEGER AS product_name_length,
        silver.blank_nan_to_null(src.product_description_lenght::TEXT)::NUMERIC::INTEGER AS product_description_length,
        silver.blank_nan_to_null(src.product_photos_qty::TEXT)::NUMERIC::INTEGER AS product_photos_qty,
        silver.blank_nan_to_null(src.product_weight_g::TEXT)::NUMERIC AS product_weight_g,
        silver.blank_nan_to_null(src.product_length_cm::TEXT)::NUMERIC AS product_length_cm,
        silver.blank_nan_to_null(src.product_height_cm::TEXT)::NUMERIC AS product_height_cm,
        silver.blank_nan_to_null(src.product_width_cm::TEXT)::NUMERIC AS product_width_cm
    FROM raw.products AS src
)
SELECT
    tp.product_id,
    tp.product_category_name,
    tp.product_name_length,
    tp.product_description_length,
    tp.product_photos_qty,
    tp.product_weight_g,
    tp.product_length_cm,
    tp.product_height_cm,
    tp.product_width_cm,
    tp.product_length_cm * tp.product_width_cm * tp.product_height_cm AS product_volume_cm3,
    gold.safe_divide(
        tp.product_weight_g,
        tp.product_length_cm * tp.product_width_cm * tp.product_height_cm
    ) AS product_density_g_per_cm3,
    (
        COALESCE(tp.product_weight_g, 0) >= 0
        AND COALESCE(tp.product_length_cm, 0) >= 0
        AND COALESCE(tp.product_height_cm, 0) >= 0
        AND COALESCE(tp.product_width_cm, 0) >= 0
    ) AS is_valid_physical_dimension
FROM typed_products AS tp;

CREATE TABLE silver.sellers AS
SELECT
    NULLIF(TRIM(src.seller_id::TEXT), '') AS seller_id,
    silver.blank_nan_to_null(src.seller_zip_code_prefix::TEXT)::NUMERIC::INTEGER AS seller_zip_code_prefix,
    LOWER(TRIM(REGEXP_REPLACE(src.seller_city::TEXT, '\s+', ' ', 'g'))) AS seller_city,
    UPPER(TRIM(src.seller_state::TEXT)) AS seller_state
FROM raw.sellers AS src;

CREATE TABLE silver.product_category_name_translation AS
SELECT
    NULLIF(LOWER(TRIM(src.product_category_name::TEXT)), '') AS product_category_name,
    NULLIF(LOWER(TRIM(src.product_category_name_english::TEXT)), '') AS product_category_name_english
FROM raw.product_category_name_translation AS src;

CREATE TABLE silver.orders AS
WITH typed_orders AS (
    SELECT
        NULLIF(TRIM(src.order_id::TEXT), '') AS order_id,
        NULLIF(TRIM(src.customer_id::TEXT), '') AS customer_id,
        LOWER(TRIM(src.order_status::TEXT)) AS order_status,
        silver.blank_nan_to_null(src.order_purchase_timestamp::TEXT)::TIMESTAMPTZ AS order_purchase_timestamp,
        silver.blank_nan_to_null(src.order_approved_at::TEXT)::TIMESTAMPTZ AS order_approved_at,
        silver.blank_nan_to_null(src.order_delivered_carrier_date::TEXT)::TIMESTAMPTZ AS order_delivered_carrier_date,
        silver.blank_nan_to_null(src.order_delivered_customer_date::TEXT)::TIMESTAMPTZ AS order_delivered_customer_date,
        silver.blank_nan_to_null(src.order_estimated_delivery_date::TEXT)::TIMESTAMPTZ AS order_estimated_delivery_date
    FROM raw.orders AS src
)
SELECT
    ord.order_id,
    ord.customer_id,
    ord.order_status,
    ord.order_purchase_timestamp,
    ord.order_approved_at,
    ord.order_delivered_carrier_date,
    ord.order_delivered_customer_date,
    ord.order_estimated_delivery_date,
    cust.customer_id IS NOT NULL AS is_customer_fk_valid,
    (
        (ord.order_approved_at IS NULL OR ord.order_purchase_timestamp IS NULL OR ord.order_approved_at >= ord.order_purchase_timestamp)
        AND (ord.order_delivered_carrier_date IS NULL OR ord.order_approved_at IS NULL OR ord.order_delivered_carrier_date >= ord.order_approved_at)
        AND (ord.order_delivered_customer_date IS NULL OR ord.order_delivered_carrier_date IS NULL OR ord.order_delivered_customer_date >= ord.order_delivered_carrier_date)
        AND (ord.order_estimated_delivery_date IS NULL OR ord.order_purchase_timestamp IS NULL OR ord.order_estimated_delivery_date >= ord.order_purchase_timestamp)
    ) AS is_temporal_sequence_valid,
    (
        ord.order_delivered_customer_date IS NOT NULL
        AND ord.order_estimated_delivery_date IS NOT NULL
        AND ord.order_delivered_customer_date > ord.order_estimated_delivery_date
    ) AS is_delivered_late
FROM typed_orders AS ord
LEFT JOIN silver.customers AS cust
  ON cust.customer_id = ord.customer_id;

CREATE TABLE silver.order_items AS
SELECT
    NULLIF(TRIM(src.order_id::TEXT), '') AS order_id,
    silver.blank_nan_to_null(src.order_item_id::TEXT)::NUMERIC::INTEGER AS order_item_id,
    NULLIF(TRIM(src.product_id::TEXT), '') AS product_id,
    NULLIF(TRIM(src.seller_id::TEXT), '') AS seller_id,
    silver.blank_nan_to_null(src.shipping_limit_date::TEXT)::TIMESTAMPTZ AS shipping_limit_date,
    silver.blank_nan_to_null(src.price::TEXT)::NUMERIC AS price,
    silver.blank_nan_to_null(src.freight_value::TEXT)::NUMERIC AS freight_value,
    COALESCE(silver.blank_nan_to_null(src.price::TEXT)::NUMERIC, 0) >= 0 AS is_price_valid,
    COALESCE(silver.blank_nan_to_null(src.freight_value::TEXT)::NUMERIC, 0) >= 0 AS is_freight_valid
FROM raw.order_items AS src;

CREATE TABLE silver.order_payments AS
WITH typed_payments AS (
    SELECT
        NULLIF(TRIM(src.order_id::TEXT), '') AS order_id,
        silver.blank_nan_to_null(src.payment_sequential::TEXT)::NUMERIC::INTEGER AS payment_sequential,
        LOWER(TRIM(src.payment_type::TEXT)) AS payment_type,
        silver.blank_nan_to_null(src.payment_installments::TEXT)::NUMERIC::INTEGER AS payment_installments,
        silver.blank_nan_to_null(src.payment_value::TEXT)::NUMERIC AS payment_value
    FROM raw.order_payments AS src
),
sequenced_payments AS (
    SELECT
        tp.order_id,
        tp.payment_sequential,
        tp.payment_type,
        tp.payment_installments,
        tp.payment_value,
        MIN(tp.payment_sequential) OVER (PARTITION BY tp.order_id) AS min_payment_sequence,
        MAX(tp.payment_sequential) OVER (PARTITION BY tp.order_id) AS max_payment_sequence,
        COUNT(*) OVER (PARTITION BY tp.order_id) AS payment_count,
        ROW_NUMBER() OVER (
            PARTITION BY tp.order_id
            ORDER BY tp.payment_sequential
        ) AS payment_row_number
    FROM typed_payments AS tp
)
SELECT
    sp.order_id,
    sp.payment_sequential,
    sp.payment_type,
    sp.payment_installments,
    sp.payment_value,
    (
        sp.min_payment_sequence = 1
        AND sp.max_payment_sequence = sp.payment_count
        AND sp.payment_sequential = sp.payment_row_number
    ) AS is_payment_sequence_valid,
    COALESCE(sp.payment_value, 0) >= 0 AS is_payment_value_valid
FROM sequenced_payments AS sp;

CREATE TABLE silver.order_reviews AS
SELECT
    NULLIF(TRIM(src.review_id::TEXT), '') AS review_id,
    NULLIF(TRIM(src.order_id::TEXT), '') AS order_id,
    silver.blank_nan_to_null(src.review_score::TEXT)::NUMERIC::INTEGER AS review_score,
    NULLIF(TRIM(src.review_comment_title::TEXT), '') AS review_comment_title,
    NULLIF(TRIM(src.review_comment_message::TEXT), '') AS review_comment_message,
    silver.blank_nan_to_null(src.review_creation_date::TEXT)::TIMESTAMPTZ AS review_creation_date,
    silver.blank_nan_to_null(src.review_answer_timestamp::TEXT)::TIMESTAMPTZ AS review_answer_timestamp,
    COUNT(*) OVER (
        PARTITION BY NULLIF(TRIM(src.review_id::TEXT), '')
    ) > 1 AS is_duplicate_review_id,
    silver.blank_nan_to_null(src.review_score::TEXT)::NUMERIC::INTEGER BETWEEN 1 AND 5 AS is_review_score_valid
FROM raw.order_reviews AS src;

CREATE TABLE silver.data_quality_issues AS
SELECT
    'silver' AS issue_layer,
    'orders' AS table_name,
    'orphan_customer_id' AS issue_type,
    ord.order_id AS issue_key,
    'orders.customer_id does not exist in customers.customer_id' AS issue_detail,
    'high' AS severity,
    NOW() AS detected_at
FROM silver.orders AS ord
WHERE ord.is_customer_fk_valid IS FALSE

UNION ALL
SELECT
    'silver' AS issue_layer,
    'orders' AS table_name,
    'invalid_temporal_sequence' AS issue_type,
    ord.order_id AS issue_key,
    'Order lifecycle timestamp order is inconsistent' AS issue_detail,
    'medium' AS severity,
    NOW() AS detected_at
FROM silver.orders AS ord
WHERE ord.is_temporal_sequence_valid IS FALSE

UNION ALL
SELECT
    'silver' AS issue_layer,
    'order_items' AS table_name,
    'orphan_order_id' AS issue_type,
    CONCAT_WS('|', item.order_id, item.order_item_id::TEXT) AS issue_key,
    'order_items.order_id does not exist in orders.order_id' AS issue_detail,
    'high' AS severity,
    NOW() AS detected_at
FROM silver.order_items AS item
LEFT JOIN silver.orders AS ord
  ON ord.order_id = item.order_id
WHERE ord.order_id IS NULL

UNION ALL
SELECT
    'silver' AS issue_layer,
    'order_items' AS table_name,
    'orphan_product_id' AS issue_type,
    CONCAT_WS('|', item.order_id, item.order_item_id::TEXT) AS issue_key,
    'order_items.product_id does not exist in products.product_id' AS issue_detail,
    'high' AS severity,
    NOW() AS detected_at
FROM silver.order_items AS item
LEFT JOIN silver.products AS prod
  ON prod.product_id = item.product_id
WHERE prod.product_id IS NULL

UNION ALL
SELECT
    'silver' AS issue_layer,
    'order_items' AS table_name,
    'orphan_seller_id' AS issue_type,
    CONCAT_WS('|', item.order_id, item.order_item_id::TEXT) AS issue_key,
    'order_items.seller_id does not exist in sellers.seller_id' AS issue_detail,
    'high' AS severity,
    NOW() AS detected_at
FROM silver.order_items AS item
LEFT JOIN silver.sellers AS sell
  ON sell.seller_id = item.seller_id
WHERE sell.seller_id IS NULL

UNION ALL
SELECT
    'silver' AS issue_layer,
    'order_items' AS table_name,
    'invalid_amount' AS issue_type,
    CONCAT_WS('|', item.order_id, item.order_item_id::TEXT) AS issue_key,
    'Item price or freight is negative' AS issue_detail,
    'medium' AS severity,
    NOW() AS detected_at
FROM silver.order_items AS item
WHERE item.is_price_valid IS FALSE
   OR item.is_freight_valid IS FALSE

UNION ALL
SELECT
    'silver' AS issue_layer,
    'order_payments' AS table_name,
    'invalid_payment_sequence' AS issue_type,
    CONCAT_WS('|', pay.order_id, pay.payment_sequential::TEXT) AS issue_key,
    'payment_sequential is not contiguous from 1 for the order' AS issue_detail,
    'medium' AS severity,
    NOW() AS detected_at
FROM silver.order_payments AS pay
WHERE pay.is_payment_sequence_valid IS FALSE

UNION ALL
SELECT
    'silver' AS issue_layer,
    'order_payments' AS table_name,
    'invalid_payment_value' AS issue_type,
    CONCAT_WS('|', pay.order_id, pay.payment_sequential::TEXT) AS issue_key,
    'payment_value is negative' AS issue_detail,
    'medium' AS severity,
    NOW() AS detected_at
FROM silver.order_payments AS pay
WHERE pay.is_payment_value_valid IS FALSE

UNION ALL
SELECT
    'silver' AS issue_layer,
    'order_payments' AS table_name,
    'orphan_order_id' AS issue_type,
    CONCAT_WS('|', pay.order_id, pay.payment_sequential::TEXT) AS issue_key,
    'order_payments.order_id does not exist in orders.order_id' AS issue_detail,
    'high' AS severity,
    NOW() AS detected_at
FROM silver.order_payments AS pay
LEFT JOIN silver.orders AS ord
  ON ord.order_id = pay.order_id
WHERE ord.order_id IS NULL

UNION ALL
SELECT
    'silver' AS issue_layer,
    'order_reviews' AS table_name,
    'duplicate_review_id' AS issue_type,
    CONCAT_WS('|', rev.review_id, rev.order_id) AS issue_key,
    'review_id appears on more than one row' AS issue_detail,
    'low' AS severity,
    NOW() AS detected_at
FROM silver.order_reviews AS rev
WHERE rev.is_duplicate_review_id IS TRUE

UNION ALL
SELECT
    'silver' AS issue_layer,
    'order_reviews' AS table_name,
    'invalid_review_score' AS issue_type,
    CONCAT_WS('|', rev.review_id, rev.order_id) AS issue_key,
    'review_score is outside the valid 1-5 range' AS issue_detail,
    'medium' AS severity,
    NOW() AS detected_at
FROM silver.order_reviews AS rev
WHERE rev.is_review_score_valid IS FALSE

UNION ALL
SELECT
    'silver' AS issue_layer,
    'order_reviews' AS table_name,
    'orphan_order_id' AS issue_type,
    CONCAT_WS('|', rev.review_id, rev.order_id) AS issue_key,
    'order_reviews.order_id does not exist in orders.order_id' AS issue_detail,
    'high' AS severity,
    NOW() AS detected_at
FROM silver.order_reviews AS rev
LEFT JOIN silver.orders AS ord
  ON ord.order_id = rev.order_id
WHERE ord.order_id IS NULL

UNION ALL
SELECT
    'silver' AS issue_layer,
    'products' AS table_name,
    'invalid_physical_dimension' AS issue_type,
    prod.product_id AS issue_key,
    'Product physical dimensions contain negative values' AS issue_detail,
    'medium' AS severity,
    NOW() AS detected_at
FROM silver.products AS prod
WHERE prod.is_valid_physical_dimension IS FALSE;

CREATE INDEX IF NOT EXISTS idx_silver_customers_customer_id
    ON silver.customers (customer_id);
CREATE INDEX IF NOT EXISTS idx_silver_customers_unique_id
    ON silver.customers (customer_unique_id);
CREATE INDEX IF NOT EXISTS idx_silver_customers_zip
    ON silver.customers (customer_zip_code_prefix);
CREATE INDEX IF NOT EXISTS idx_silver_geolocation_zip
    ON silver.geolocation_zip_prefixes (geolocation_zip_code_prefix);
CREATE INDEX IF NOT EXISTS idx_silver_orders_order_id
    ON silver.orders (order_id);
CREATE INDEX IF NOT EXISTS idx_silver_orders_customer_id
    ON silver.orders (customer_id);
CREATE INDEX IF NOT EXISTS idx_silver_orders_purchase_ts
    ON silver.orders (order_purchase_timestamp);
CREATE INDEX IF NOT EXISTS idx_silver_order_items_order_id
    ON silver.order_items (order_id);
CREATE INDEX IF NOT EXISTS idx_silver_order_items_product_id
    ON silver.order_items (product_id);
CREATE INDEX IF NOT EXISTS idx_silver_order_items_seller_id
    ON silver.order_items (seller_id);
CREATE INDEX IF NOT EXISTS idx_silver_order_payments_order_id
    ON silver.order_payments (order_id);
CREATE INDEX IF NOT EXISTS idx_silver_order_reviews_order_id
    ON silver.order_reviews (order_id);
CREATE INDEX IF NOT EXISTS idx_silver_products_product_id
    ON silver.products (product_id);
CREATE INDEX IF NOT EXISTS idx_silver_sellers_seller_id
    ON silver.sellers (seller_id);
CREATE INDEX IF NOT EXISTS idx_silver_sellers_zip
    ON silver.sellers (seller_zip_code_prefix);
CREATE INDEX IF NOT EXISTS idx_silver_quality_issue_type
    ON silver.data_quality_issues (issue_type);
