-- Silver Order Reviews: Cleaned & Incremental Upsert
CREATE UNLOGGED TABLE IF NOT EXISTS silver.order_reviews (
    review_id TEXT,
    order_id TEXT,
    review_score INTEGER,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP,
    _last_updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (review_id, order_id)
);

CREATE TEMP TABLE stg_order_reviews_cleaned AS
SELECT
    NULLIF(TRIM(review_id::TEXT), '') AS review_id,
    NULLIF(TRIM(order_id::TEXT), '') AS order_id,
    NULLIF(TRIM(review_score::TEXT), '')::NUMERIC::INTEGER AS review_score,
    NULLIF(TRIM(review_comment_title::TEXT), '') AS review_comment_title,
    NULLIF(TRIM(review_comment_message::TEXT), '') AS review_comment_message,
    NULLIF(TRIM(review_creation_date::TEXT), '')::TIMESTAMP AS review_creation_date,
    NULLIF(TRIM(review_answer_timestamp::TEXT), '')::TIMESTAMP AS review_answer_timestamp
FROM bronze.order_reviews;

INSERT INTO silver.order_reviews (
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date,
    review_answer_timestamp,
    _last_updated_at
)
SELECT 
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date,
    review_answer_timestamp,
    NOW()
FROM stg_order_reviews_cleaned
ON CONFLICT (review_id, order_id) 
DO UPDATE SET
    review_score = EXCLUDED.review_score,
    review_comment_title = EXCLUDED.review_comment_title,
    review_comment_message = EXCLUDED.review_comment_message,
    review_creation_date = EXCLUDED.review_creation_date,
    review_answer_timestamp = EXCLUDED.review_answer_timestamp,
    _last_updated_at = NOW();

CREATE INDEX IF NOT EXISTS idx_silver_order_reviews_score ON silver.order_reviews(review_score);

COMMENT ON TABLE silver.order_reviews IS 'Cleaned customer review fact table.';
