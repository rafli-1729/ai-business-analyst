DROP TABLE IF EXISTS gold.review_summary CASCADE;

CREATE TABLE gold.review_summary AS

SELECT
    DATE_TRUNC(
        'month',
        o.order_purchase_timestamp
    ) AS month,

    AVG(orv.review_score)
        AS avg_review_score,

    COUNT(*) AS total_reviews,

    AVG(
        CASE
            WHEN orv.review_score <= 2
            THEN 1
            ELSE 0
        END
    ) AS negative_review_rate,

    AVG(
        CASE
            WHEN orv.review_score >= 4
            THEN 1
            ELSE 0
        END
    ) AS positive_review_rate

FROM silver.order_reviews AS orv

JOIN silver.orders AS o
    ON orv.order_id = o.order_id

GROUP BY 1;

CREATE INDEX idx_gold_review_summary_month
ON gold.review_summary(month);

COMMENT ON TABLE gold.review_summary IS
'Monthly customer review and satisfaction mart.';