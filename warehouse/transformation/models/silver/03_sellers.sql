-- Silver Sellers: Normalized & Incremental Upsert (Join-based)
CREATE UNLOGGED TABLE IF NOT EXISTS silver.sellers (
    seller_id TEXT PRIMARY KEY,
    seller_zip_code_prefix INTEGER,
    seller_city TEXT,
    seller_state TEXT,
    _last_updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TEMP TABLE stg_sellers_cleaned AS
SELECT
    NULLIF(TRIM(b.seller_id::TEXT), '') AS seller_id,
    NULLIF(TRIM(b.seller_zip_code_prefix::TEXT), '')::INTEGER AS seller_zip_code_prefix,
    COALESCE(gm.canonical_city, TRIM(b.seller_city)) AS seller_city,
    COALESCE(gm.state, UPPER(TRIM(b.seller_state))) AS seller_state
FROM bronze.sellers b
LEFT JOIN master.geography_master gm 
    ON TRIM(b.seller_city) = gm.raw_city AND UPPER(TRIM(b.seller_state)) = gm.state;

INSERT INTO silver.sellers (
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state,
    _last_updated_at
)
SELECT 
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state,
    NOW()
FROM stg_sellers_cleaned
ON CONFLICT (seller_id) 
DO UPDATE SET
    seller_zip_code_prefix = EXCLUDED.seller_zip_code_prefix,
    seller_city = EXCLUDED.seller_city,
    seller_state = EXCLUDED.seller_state,
    _last_updated_at = NOW();

CREATE INDEX IF NOT EXISTS idx_silver_sellers_state ON silver.sellers(seller_state);

COMMENT ON TABLE silver.sellers IS 'Cleaned seller dimension table with normalized geography.';
COMMENT ON COLUMN silver.sellers.seller_id IS 'Primary Key. Unique identifier for the seller.';
COMMENT ON COLUMN silver.sellers.seller_zip_code_prefix IS 'Five digit zip code prefix of the seller.';
COMMENT ON COLUMN silver.sellers.seller_city IS 'Normalized city name where the seller is located. Format: Title Case (e.g., "São Paulo"), UTF-8 encoded.';
COMMENT ON COLUMN silver.sellers.seller_state IS 'State abbreviation of the seller.';
