DROP TABLE IF EXISTS silver.products CASCADE;

CREATE TABLE silver.products AS

SELECT
    NULLIF(
        TRIM(product_id::TEXT),
        ''
    ) AS product_id,

    LOWER(
        TRIM(product_category_name::TEXT)
    ) AS product_category_name,

    product_name_lenght::INTEGER AS product_name_length,

    product_description_lenght::INTEGER AS product_description_length,

    product_photos_qty::INTEGER AS product_photos_qty,

    product_weight_g::NUMERIC AS product_weight_g,

    product_length_cm::NUMERIC AS product_length_cm,

    product_height_cm::NUMERIC AS product_height_cm,

    product_width_cm::NUMERIC AS product_width_cm

FROM bronze.products;

ALTER TABLE silver.products
ADD PRIMARY KEY(product_id);

CREATE INDEX idx_silver_products_category
ON silver.products(product_category_name);

COMMENT ON TABLE silver.products IS
'Cleaned product dimension table.';

COMMENT ON COLUMN silver.products.product_category_name IS
'Normalized Portuguese product category name.';