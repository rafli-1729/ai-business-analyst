DROP TABLE IF EXISTS silver.order_reviews CASCADE;

CREATE TABLE silver.order_reviews AS

SELECT
    NULLIF(
        TRIM(review_id::TEXT),
        ''
    ) AS review_id,

    NULLIF(
        TRIM(order_id::TEXT),
        ''
    ) AS order_id,

    review_score::INTEGER
        AS review_score,

    silver.blank_nan_to_null(
        review_comment_title::TEXT
    ) AS review_comment_title,

    silver.blank_nan_to_null(
        review_comment_message::TEXT
    ) AS review_comment_message,

    review_creation_date::TIMESTAMP
        AS review_creation_date,

    review_answer_timestamp::TIMESTAMP
        AS review_answer_timestamp

FROM bronze.order_reviews;

ALTER TABLE silver.order_reviews
ADD PRIMARY KEY(
    review_id,
    order_id
);

ALTER TABLE silver.order_reviews
ADD CONSTRAINT fk_order_reviews_order
FOREIGN KEY(order_id)
REFERENCES silver.orders(order_id);

CREATE INDEX idx_silver_order_reviews_score
ON silver.order_reviews(review_score);

COMMENT ON TABLE silver.order_reviews IS
'Cleaned customer review fact table.';

COMMENT ON COLUMN silver.order_reviews.review_score IS
'Customer satisfaction score ranging from 1 to 5.';

COMMENT ON COLUMN silver.order_reviews.review_comment_message IS
'Optional free-text customer review.';