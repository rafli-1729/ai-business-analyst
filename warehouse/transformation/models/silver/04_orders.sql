DROP TABLE IF EXISTS silver.orders CASCADE;

CREATE TABLE silver.orders AS

SELECT
    NULLIF(
        TRIM(order_id::TEXT),
        ''
    ) AS order_id,

    NULLIF(
        TRIM(customer_id::TEXT),
        ''
    ) AS customer_id,

    LOWER(
        TRIM(order_status::TEXT)
    ) AS order_status,

    order_purchase_timestamp::TIMESTAMP
        AS order_purchase_timestamp,

    order_approved_at::TIMESTAMP
        AS order_approved_at,

    order_delivered_carrier_date::TIMESTAMP
        AS order_delivered_carrier_date,

    order_delivered_customer_date::TIMESTAMP
        AS order_delivered_customer_date,

    order_estimated_delivery_date::TIMESTAMP
        AS order_estimated_delivery_date

FROM bronze.orders;

ALTER TABLE silver.orders
ADD PRIMARY KEY(order_id);

ALTER TABLE silver.orders
ADD CONSTRAINT fk_orders_customer
FOREIGN KEY(customer_id)
REFERENCES silver.customers(customer_id);

CREATE INDEX idx_silver_orders_customer_id
ON silver.orders(customer_id);

CREATE INDEX idx_silver_orders_purchase_timestamp
ON silver.orders(order_purchase_timestamp);

CREATE INDEX idx_silver_orders_status
ON silver.orders(order_status);

COMMENT ON TABLE silver.orders IS
'Cleaned transactional orders fact table.';

COMMENT ON COLUMN silver.orders.order_purchase_timestamp IS
'Timestamp when customer placed the order.';