DROP TABLE IF EXISTS silver.customers CASCADE;

CREATE TABLE silver.customers AS

WITH cleaned AS (

    SELECT
        NULLIF(
            TRIM(customer_id::TEXT),
            ''
        ) AS customer_id,

        NULLIF(
            TRIM(customer_unique_id::TEXT),
            ''
        ) AS customer_unique_id,

        NULLIF(
            TRIM(customer_zip_code_prefix::TEXT),
            ''
        )::INTEGER AS customer_zip_code_prefix,

        LOWER(
            TRIM(
                REGEXP_REPLACE(
                    customer_city::TEXT,
                    '\s+',
                    ' ',
                    'g'
                )
            )
        ) AS customer_city,

        UPPER(
            TRIM(customer_state::TEXT)
        ) AS customer_state

    FROM bronze.customers
),

deduplicated AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY customer_unique_id
        ) AS row_rank

    FROM cleaned
)

SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state

FROM deduplicated

WHERE row_rank = 1;

ALTER TABLE silver.customers
ADD PRIMARY KEY(customer_id);

CREATE INDEX idx_silver_customers_unique_id
ON silver.customers(customer_unique_id);

CREATE INDEX idx_silver_customers_state
ON silver.customers(customer_state);

COMMENT ON TABLE silver.customers IS
'Cleaned and deduplicated customer dimension table.';

COMMENT ON COLUMN silver.customers.customer_id IS
'Unique order-level customer identifier.';

COMMENT ON COLUMN silver.customers.customer_unique_id IS
'Persistent customer identifier across multiple orders.';

COMMENT ON COLUMN silver.customers.customer_city IS
'Normalized lowercase customer city name.';

COMMENT ON COLUMN silver.customers.customer_state IS
'Brazilian state abbreviation.';