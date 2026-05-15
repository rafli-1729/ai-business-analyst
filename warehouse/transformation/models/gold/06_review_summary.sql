-- =========================================================
-- gold/06_review_summary.sql
-- =========================================================

DROP TABLE IF EXISTS gold.review_summary CASCADE;

CREATE TABLE gold.review_summary AS

SELECT
    DATE(
        o.order_purchase_timestamp
    ) AS purchase_date,

    AVG(orv.review_score)
        AS average_review_score,

    COUNT(*)
        AS total_reviews,

    AVG(
        CASE
            WHEN orv.review_score <= 2
            THEN 1
            ELSE 0
        END
    ) AS negative_review_rate

FROM silver.order_reviews AS orv

JOIN silver.orders AS o
    ON orv.order_id = o.order_id

GROUP BY 1;

COMMENT ON TABLE gold.review_summary IS
'Daily customer review and satisfaction mart.';