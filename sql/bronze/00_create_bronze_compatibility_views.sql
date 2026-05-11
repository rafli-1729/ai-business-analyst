CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;
CREATE SCHEMA IF NOT EXISTS ops;

CREATE OR REPLACE FUNCTION silver.blank_nan_to_null(value TEXT)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT CASE
        WHEN value IS NULL THEN NULL
        WHEN BTRIM(value) = '' THEN NULL
        WHEN LOWER(BTRIM(value)) = 'nan' THEN NULL
        ELSE BTRIM(value)
    END
$$;

CREATE OR REPLACE FUNCTION gold.safe_divide(numerator NUMERIC, denominator NUMERIC)
RETURNS NUMERIC
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT CASE
        WHEN denominator IS NULL OR denominator = 0 THEN NULL
        ELSE numerator / denominator
    END
$$;

CREATE OR REPLACE FUNCTION gold.haversine_km(
    lat_1 DOUBLE PRECISION,
    lng_1 DOUBLE PRECISION,
    lat_2 DOUBLE PRECISION,
    lng_2 DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT CASE
        WHEN lat_1 IS NULL
          OR lng_1 IS NULL
          OR lat_2 IS NULL
          OR lng_2 IS NULL
        THEN NULL
        ELSE
            6371.0 * 2.0 * ASIN(
                SQRT(
                    POWER(SIN(RADIANS(lat_2 - lat_1) / 2.0), 2)
                    + COS(RADIANS(lat_1))
                    * COS(RADIANS(lat_2))
                    * POWER(SIN(RADIANS(lng_2 - lng_1) / 2.0), 2)
                )
            )
    END
$$;

DO $$
DECLARE
    v_source_table_name TEXT;
    v_source_schema TEXT;
    v_column_list TEXT;
    source_tables TEXT[] := ARRAY[
        'customers',
        'geolocation',
        'orders',
        'order_items',
        'order_payments',
        'order_reviews',
        'products',
        'sellers',
        'product_category_name_translation'
    ];
BEGIN
    FOREACH v_source_table_name IN ARRAY source_tables
    LOOP
        IF EXISTS (
            SELECT 1
            FROM pg_class AS c
            JOIN pg_namespace AS n
              ON n.oid = c.relnamespace
            WHERE n.nspname = 'bronze'
              AND c.relname = v_source_table_name
              AND c.relkind IN ('r', 'p')
        )
        THEN
            v_source_schema := 'bronze';
        ELSIF EXISTS (
            SELECT 1
            FROM pg_class AS c
            JOIN pg_namespace AS n
              ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relname = v_source_table_name
              AND c.relkind IN ('r', 'p')
        )
        THEN
            v_source_schema := 'public';
        ELSE
            CONTINUE;
        END IF;

        SELECT STRING_AGG(FORMAT('%I', c.column_name), ', ' ORDER BY c.ordinal_position)
        INTO v_column_list
        FROM information_schema.columns AS c
        WHERE c.table_schema = v_source_schema
          AND c.table_name = v_source_table_name
          AND c.column_name NOT IN (
              '_ingested_at',
              '_source_file',
              '_source_checksum',
              '_ingestion_run_id'
          );

        IF v_column_list IS NULL THEN
            CONTINUE;
        END IF;

        EXECUTE FORMAT('DROP VIEW IF EXISTS raw.%I CASCADE', v_source_table_name);

        EXECUTE FORMAT(
            'CREATE VIEW raw.%I AS SELECT %s FROM %I.%I',
            v_source_table_name,
            v_column_list,
            v_source_schema,
            v_source_table_name
        );
    END LOOP;
END $$;
