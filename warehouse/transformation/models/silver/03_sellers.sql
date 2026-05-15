DROP TABLE IF EXISTS silver.sellers CASCADE;

CREATE TABLE silver.sellers AS

SELECT
    NULLIF(
        TRIM(seller_id::TEXT),
        ''
    ) AS seller_id,

    NULLIF(
        TRIM(seller_zip_code_prefix::TEXT),
        ''
    )::INTEGER AS seller_zip_code_prefix,

    LOWER(
        TRIM(
            REGEXP_REPLACE(
                seller_city::TEXT,
                '\s+',
                ' ',
                'g'
            )
        )
    ) AS seller_city,

    UPPER(
        TRIM(seller_state::TEXT)
    ) AS seller_state

FROM bronze.sellers;

ALTER TABLE silver.sellers
ADD PRIMARY KEY(seller_id);

CREATE INDEX idx_silver_sellers_state
ON silver.sellers(seller_state);

COMMENT ON TABLE silver.sellers IS
'Cleaned seller dimension table.';