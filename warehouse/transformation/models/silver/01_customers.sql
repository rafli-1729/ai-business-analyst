-- Silver Customers: Normalized & Incremental Upsert (Join-based)
CREATE UNLOGGED TABLE IF NOT EXISTS silver.customers (
    customer_id TEXT PRIMARY KEY,
    customer_unique_id TEXT,
    customer_zip_code_prefix INTEGER,
    customer_city TEXT,
    customer_state TEXT,
    _last_updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Staging cleaned data
CREATE TEMP TABLE stg_customers_cleaned AS
WITH base AS (
    SELECT
        NULLIF(TRIM(b.customer_id::TEXT), '') AS customer_id,
        NULLIF(TRIM(b.customer_unique_id::TEXT), '') AS customer_unique_id,
        NULLIF(TRIM(b.customer_zip_code_prefix::TEXT), '')::INTEGER AS customer_zip_code_prefix,
        COALESCE(gm.canonical_city, TRIM(b.customer_city)) AS customer_city,
        COALESCE(gm.state, UPPER(TRIM(b.customer_state))) AS customer_state
    FROM bronze.customers b
    LEFT JOIN master.geography_master gm 
        ON TRIM(b.customer_city) = gm.raw_city AND UPPER(TRIM(b.customer_state)) = gm.state
),
deduplicated AS (
    SELECT
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY customer_unique_id
        ) AS row_rank
    FROM base
)
SELECT * FROM deduplicated WHERE row_rank = 1;

-- Incremental Upsert
INSERT INTO silver.customers (
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,
    _last_updated_at
)
SELECT 
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,
    NOW()
FROM stg_customers_cleaned
ON CONFLICT (customer_id) 
DO UPDATE SET
    customer_unique_id = EXCLUDED.customer_unique_id,
    customer_zip_code_prefix = EXCLUDED.customer_zip_code_prefix,
    customer_city = EXCLUDED.customer_city,
    customer_state = EXCLUDED.customer_state,
    _last_updated_at = NOW();

CREATE INDEX IF NOT EXISTS idx_silver_customers_unique_id ON silver.customers(customer_unique_id);
CREATE INDEX IF NOT EXISTS idx_silver_customers_state ON silver.customers(customer_state);

COMMENT ON TABLE silver.customers IS 'Cleaned and deduplicated customer dimension table with Master Geography normalization.';
COMMENT ON COLUMN silver.customers.customer_id IS 'Primary Key. Link to the specific customer record in the raw orders data.';
COMMENT ON COLUMN silver.customers.customer_unique_id IS 'Unique identifier for the buyer, remains consistent across multiple orders.';
COMMENT ON COLUMN silver.customers.customer_zip_code_prefix IS 'Five digit zip code prefix of the buyer.';
COMMENT ON COLUMN silver.customers.customer_city IS 'Normalized city name of the buyer. Format: Title Case (e.g., "Rio de Janeiro"), UTF-8 encoded.';
COMMENT ON COLUMN silver.customers.customer_state IS 'State abbreviation of the buyer.';
