SCHEMA = """

DATABASE OVERVIEW:
This database contains Brazilian e-commerce transaction data from Olist.
The data includes customers, orders, products, payments, reviews, sellers, and geolocation information.


==================================================
TABLE: customers
==================================================

Description:
Contains customer identity and customer location information.

Columns:
- customer_id:
  Order-level customer identifier.
  One customer can have multiple customer_id values.

- customer_unique_id:
  Persistent unique customer identity across multiple orders.
  Use this field for repeat customer analysis.

- customer_zip_code_prefix:
  Customer ZIP code prefix.

- customer_city:
  Customer city.

- customer_state:
  Customer state abbreviation in Brazil.

Sample Data:
customer_city | customer_state
sao paulo     | SP


==================================================
TABLE: geolocation
==================================================

Description:
Contains ZIP code geolocation mapping.

Columns:
- geolocation_zip_code_prefix:
  ZIP code prefix.

- geolocation_lat:
  Latitude coordinate.

- geolocation_lng:
  Longitude coordinate.

- geolocation_city:
  City name.

- geolocation_state:
  State abbreviation.


==================================================
TABLE: orders
==================================================

Description:
Contains order lifecycle information and timestamps.

Columns:
- order_id:
  Unique order identifier.

- customer_id:
  Foreign key to customers table.

- order_status:
  Current order status.

- order_purchase_timestamp:
  Timestamp when the order was placed.

- order_approved_at:
  Timestamp when payment was approved.

- order_delivered_carrier_date:
  Timestamp when order was handed to carrier.

- order_delivered_customer_date:
  Timestamp when customer received the order.

- order_estimated_delivery_date:
  Estimated delivery date.


==================================================
TABLE: order_items
==================================================

Description:
Contains item-level transaction details for each order.

Columns:
- order_id:
  Foreign key to orders table.

- order_item_id:
  Sequential item number inside an order.

- product_id:
  Foreign key to products table.

- seller_id:
  Foreign key to sellers table.

- shipping_limit_date:
  Shipping deadline timestamp.

- price:
  Product price excluding shipping cost.

- freight_value:
  Shipping cost for the item.


==================================================
TABLE: order_payments
==================================================

Description:
Contains payment information for each order.

Columns:
- order_id:
  Foreign key to orders table.

- payment_sequential:
  Payment sequence number.

- payment_type:
  Payment method used by customer.

- payment_installments:
  Number of installments.

- payment_value:
  Total payment amount for the order.


==================================================
TABLE: order_reviews
==================================================

Description:
Contains customer review and satisfaction information.

Columns:
- review_id:
  Unique review identifier.

- order_id:
  Foreign key to orders table.

- review_score:
  Customer review score from 1 to 5.

- review_comment_title:
  Review title.

- review_comment_message:
  Review text message.

- review_creation_date:
  Review creation date.

- review_answer_timestamp:
  Timestamp when review was answered.


==================================================
TABLE: products
==================================================

Description:
Contains product metadata and physical dimensions.

Columns:
- product_id:
  Unique product identifier.

- product_category_name:
  Product category in Portuguese.

- product_name_lenght:
  Length of product name text.

- product_description_lenght:
  Length of product description text.

- product_photos_qty:
  Number of product photos.

- product_weight_g:
  Product weight in grams.

- product_length_cm:
  Product length in centimeters.

- product_height_cm:
  Product height in centimeters.

- product_width_cm:
  Product width in centimeters.


==================================================
TABLE: sellers
==================================================

Description:
Contains seller and merchant location information.

Columns:
- seller_id:
  Unique seller identifier.

- seller_zip_code_prefix:
  Seller ZIP code prefix.

- seller_city:
  Seller city.

- seller_state:
  Seller state abbreviation.


==================================================
TABLE: product_category_name_translation
==================================================

Description:
Maps Portuguese product category names to English translations.

Columns:
- product_category_name:
  Product category in Portuguese.

- product_category_name_english:
  English translation of category name.


==================================================
RELATIONSHIPS
==================================================

- orders.customer_id -> customers.customer_id
- order_items.order_id -> orders.order_id
- order_items.product_id -> products.product_id
- order_items.seller_id -> sellers.seller_id
- order_payments.order_id -> orders.order_id
- order_reviews.order_id -> orders.order_id
- products.product_category_name
-> product_category_name_translation.product_category_name


==================================================
BUSINESS RULES
==================================================

- Use customer_unique_id for repeat customer analysis.
- Prefer human-readable fields over raw IDs, never return raw IDs.
- Prefer English category names when available.
- payment_value represents total transaction amount.
- price excludes shipping fee.
- freight_value represents shipping cost.
- review_score ranges from 1 (worst) to 5 (best).
- Use DATE_TRUNC for monthly or yearly trend analysis.
- order_purchase_timestamp is the main purchase timestamp.
- If no product name exists, use product category as product representation
- Aggregate results at the business-friendly level unless user explicitly asks for technical IDs

"""