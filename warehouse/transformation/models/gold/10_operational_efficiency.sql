-- =========================================================
-- gold/10_operational_efficiency.sql
-- =========================================================

DROP TABLE IF EXISTS gold.operational_efficiency CASCADE;

CREATE TABLE gold.operational_efficiency AS

SELECT
    seller_id,

    AVG(freight_value)
        AS average_freight_value,

    AVG(price)
        AS average_item_price,

    COUNT(*)
        AS total_items_shipped

FROM silver.order_items

GROUP BY 1;

COMMENT ON TABLE gold.operational_efficiency IS
'Seller operational shipping and pricing efficiency mart.';