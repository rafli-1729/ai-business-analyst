-- Master Geography: Aggregated and Unified (Pure SQL Transformation)
SET default_transaction_read_only = off;
CREATE SCHEMA IF NOT EXISTS master;

CREATE TABLE IF NOT EXISTS master.geography (
    city TEXT,
    state TEXT,
    avg_lat NUMERIC,
    avg_lng NUMERIC,
    _last_updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (city, state)
);

-- Process raw geolocation if it exists
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'reference' AND table_name = 'geolocation') THEN
        INSERT INTO master.geography (city, state, avg_lat, avg_lng, _last_updated_at)
        WITH raw_cleaned AS (
            SELECT 
                -- Robust Normalization: No accents, Initcap, Remove district suffix
                INITCAP(TRIM(TRANSLATE(LOWER(SPLIT_PART(SPLIT_PART(geolocation_city, '-', 1), '(', 1)), 'áàâãéêíóôõúç', 'aaaaeeiooouc'))) as city,
                UPPER(TRIM(geolocation_state)) as state,
                -- Explicitly casting TEXT to NUMERIC (since Bronze is now all TEXT)
                NULLIF(TRIM(geolocation_lat), '')::NUMERIC as lat,
                NULLIF(TRIM(geolocation_lng), '')::NUMERIC as lng
            FROM reference.geolocation
        ),
        aggregated AS (
            SELECT 
                city, 
                state, 
                AVG(lat) as avg_lat, 
                AVG(lng) as avg_lng
            FROM raw_cleaned
            WHERE city IS NOT NULL AND city != ''
            GROUP BY 1, 2
        )
        SELECT city, state, avg_lat, avg_lng, NOW() FROM aggregated
        ON CONFLICT (city, state) DO UPDATE SET
            avg_lat = EXCLUDED.avg_lat,
            avg_lng = EXCLUDED.avg_lng,
            _last_updated_at = NOW();

        -- Drop the massive table after processing to save disk
        DROP TABLE reference.geolocation;
    END IF;
END $$;

COMMENT ON TABLE master.geography IS 'Unified Brazilian geography master data with aggregated coordinates.';
