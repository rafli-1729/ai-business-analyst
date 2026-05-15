DROP TABLE IF EXISTS silver.order_items CASCADE;

CREATE TABLE silver.order_items AS

SELECT
    NULLIF(
        TRIM(order_id::TEXT),
        ''
    ) AS order_id,

    order_item_id::INTEGER AS order_item_id,

    NULLIF(
        TRIM(product_id::TEXT),
        ''
    ) AS product_id,

    NULLIF(
        TRIM(seller_id::TEXT),
        ''
    ) AS seller_id,

    shipping_limit_date::TIMESTAMP
        AS shipping_limit_date,

    price::NUMERIC AS price,

    freight_value::NUMERIC AS freight_value

FROM bronze.order_items;

ALTER TABLE silver.order_items
ADD PRIMARY KEY(order_id, order_item_id);

ALTER TABLE silver.order_items
ADD CONSTRAINT fk_order_items_order
FOREIGN KEY(order_id)
REFERENCES silver.orders(order_id);

ALTER TABLE silver.order_items
ADD CONSTRAINT fk_order_items_product
FOREIGN KEY(product_id)
REFERENCES silver.products(product_id);

ALTER TABLE silver.order_items
ADD CONSTRAINT fk_order_items_seller
FOREIGN KEY(seller_id)
REFERENCES silver.sellers(seller_id);

CREATE INDEX idx_silver_order_items_product
ON silver.order_items(product_id);

CREATE INDEX idx_silver_order_items_seller
ON silver.order_items(seller_id);

COMMENT ON TABLE silver.order_items IS
'Cleaned order item level transactional fact table.';

COMMENT ON COLUMN silver.order_items.price IS
'Product price excluding freight cost.';

COMMENT ON COLUMN silver.order_items.freight_value IS
'Shipping cost paid for the order item.';