# Olist Brazilian E-Commerce Dataset

Schema version: 2026-05-10

Relational e-commerce business warehouse containing customers, orders, products, sellers, payments, reviews, and geolocation data.

Business domain: E-Commerce Analytics

## Main use cases
- Revenue analysis
- Customer behavior analysis
- Delivery performance analysis
- Product category analysis
- Seller performance analysis
- Payment behavior analysis
- Review and satisfaction analysis

## Warehouse layers
- bronze: Bronze / Immutable Raw - Source-aligned Olist tables loaded with minimal cleaning plus ingestion metadata columns.
- raw: Raw Compatibility Views - Compatibility views over bronze/public source tables with ingestion metadata columns hidden.
- silver: Silver / Standardized - Typed, normalized, and quality-flagged relational tables built inside PostgreSQL from raw data.
- gold: Gold / AI Analytics Serving - Wide denormalized serving facts plus secondary aggregate marts optimized for natural-language analytics.

## Recommended analytics tables
### Analytics table: gold.order_item_facts
Layer: gold
Grain: One row per order item.
Description: Primary LLM-friendly analytical serving table. It denormalizes order, item, customer, seller, product, payment, review, logistics, geography, and feature-engineered metrics.
Preferred for:
- Default table for business analytics questions
- Text-to-SQL and LLM-powered analysis
- Detailed revenue, delivery, customer, seller, product, payment, and geography analysis
- Dashboard serving without repeated multi-table joins
Columns:
- order_id (identifier): Order identifier.
- order_item_id (identifier): Item sequence number inside an order.
- product_category_name (categorical): Business-friendly product category, preferring English translation.
- customer_state (location): Customer Brazilian state abbreviation.
- seller_state (location): Seller Brazilian state abbreviation.
- purchase_month_start_date (date): Month of order purchase.
- order_item_revenue (metric): Item price excluding freight.
- order_item_shipping_cost (metric): Shipping cost for the item.
- total_order_item_cost (metric): Item price plus freight value.
- customer_satisfaction_score (metric): Average order review score attached to the item, named for business interpretation.
- delivery_distance_km (metric): Haversine distance between customer and seller ZIP prefix coordinates.
- delivery_efficiency_score (metric): Estimated delivery days divided by actual delivery days; higher values indicate faster-than-estimated delivery.
- customer_rfm_score (metric): Combined recency, frequency, and monetary score for customer behavior analysis.
- seller_revenue_rank (metric): Seller rank by total item revenue.
- product_return_risk_proxy (metric): Proxy risk based on low review score or late delivery.
- is_delivered_late (boolean): Whether delivered date is later than estimated date.

### Analytics table: gold.monthly_revenue
Layer: gold
Grain: One row per purchase month.
Description: Monthly revenue, order, customer, review, and late-delivery summary.
Preferred for:
- Monthly revenue trend
- Growth analysis
- KPI cards by month
Columns:
- purchase_month (date): Month of order purchase.
- total_orders (metric): Distinct order count.
- unique_customers (metric): Distinct repeat-customer identity count.
- total_revenue (metric): Sum of item prices excluding freight.
- total_order_item_cost (metric): Sum of item prices plus freight.
- customer_satisfaction_score (metric): Average review score.

### Analytics table: gold.category_performance
Layer: gold
Grain: One row per translated product category.
Description: Product category revenue and satisfaction summary.
Preferred for:
- Top product categories
- Category revenue ranking
- Category satisfaction comparison
Columns:
- product_category_name (categorical): English translated product category when available.
- total_orders (metric): Distinct order count.
- total_revenue (metric): Sum of item prices excluding freight.
- total_order_item_cost (metric): Sum of item prices plus freight.
- customer_satisfaction_score (metric): Average review score.

### Analytics table: gold.state_performance
Layer: gold
Grain: One row per customer state.
Description: Customer state level revenue and delivery summary.
Preferred for:
- State revenue ranking
- Regional demand analysis
- Late delivery by customer state
Columns:
- customer_state (location): Customer Brazilian state abbreviation.
- total_orders (metric): Distinct order count.
- unique_customers (metric): Distinct repeat-customer identity count.
- total_revenue (metric): Sum of item prices excluding freight.
- late_delivery_rate (metric): Share of item rows attached to late deliveries.

### Analytics table: gold.seller_performance
Layer: gold
Grain: One row per seller.
Description: Seller-level revenue, volume, review, and delivery performance.
Preferred for:
- Seller ranking
- Seller revenue analysis
- Seller delivery and satisfaction comparison
Columns:
- seller_id (identifier): Seller identifier. Avoid returning unless explicitly requested.
- seller_city (location): Normalized seller city.
- seller_state (location): Seller Brazilian state abbreviation.
- total_revenue (metric): Sum of item prices excluding freight.
- customer_satisfaction_score (metric): Average review score.

### Analytics table: gold.payment_method_performance
Layer: gold
Grain: One row per payment type.
Description: Payment method usage and payment value summary.
Preferred for:
- Payment method comparison
- Average payment value
- Installment behavior analysis
Columns:
- payment_type (categorical): Customer payment method.
- total_orders (metric): Distinct order count.
- payment_value (metric): Total payment value.
- avg_payment_value (metric): Average payment value.
- avg_installments (metric): Average number of installments.

### Analytics table: gold.delivery_performance
Layer: gold
Grain: One row per purchase month and customer state.
Description: Monthly delivery speed and lateness summary by customer state.
Preferred for:
- Delivery delay analysis
- Average delivery time
- Regional logistics comparison
Columns:
- purchase_month (date): Month of order purchase.
- customer_state (location): Customer Brazilian state abbreviation.
- total_orders (metric): Distinct order count.
- late_orders (metric): Number of late delivered orders.
- avg_delivery_days (metric): Average days from purchase to delivered customer date.

### Analytics table: silver.data_quality_issues
Layer: silver
Grain: One row per detected data quality issue.
Description: Formalized validation findings derived from the preparation notebook.
Preferred for:
- Data quality checks
- Validation audit
- Explaining records excluded or flagged before analytics
Columns:
- table_name (categorical): Table where the issue was detected.
- issue_type (categorical): Machine-readable issue name.
- issue_key (identifier): Relevant record key for the issue.
- severity (categorical): Issue severity.

## Source and warehouse tables
### Table: customers
Description: Customer identity and customer location information.
Business rules:
- Use customer_unique_id for repeat customer analysis.
- One customer_unique_id may have multiple customer_id values.
Columns:
- customer_id (identifier): Order-level customer identifier.
- customer_unique_id (business_identifier): Persistent customer identity across multiple orders.
- customer_zip_code_prefix (location): Customer ZIP code prefix.
- customer_city (location): Customer city.
- customer_state (location): Brazilian state abbreviation.

### Table: orders
Description: Order lifecycle and operational timestamps.
Business rules:
- order_purchase_timestamp is the main purchase timestamp.
- Use DATE_TRUNC for monthly or yearly trend analysis.
Columns:
- order_id (identifier): Unique order identifier.
- customer_id (foreign_key): Foreign key to customers table.
- order_status (categorical): Current order status.
- order_purchase_timestamp (timestamp): Timestamp when the order was placed.
- order_approved_at (timestamp): Timestamp when payment was approved.
- order_delivered_carrier_date (timestamp): Timestamp when order was handed to carrier.
- order_delivered_customer_date (timestamp): Timestamp when customer received the order.
- order_estimated_delivery_date (timestamp): Estimated delivery date.

### Table: order_items
Description: Item-level transaction details for each order.
Business rules:
- price excludes shipping cost.
- freight_value represents shipping cost.
Columns:
- order_id (foreign_key): Foreign key to orders table.
- order_item_id (identifier): Sequential item number inside an order.
- product_id (foreign_key): Foreign key to products table.
- seller_id (foreign_key): Foreign key to sellers table.
- shipping_limit_date (timestamp): Shipping deadline timestamp.
- price (metric): Product selling price excluding shipping.
- freight_value (metric): Shipping cost for the item.

### Table: order_payments
Description: Payment information for each order.
Business rules:
- payment_value represents total transaction amount.
Columns:
- order_id (foreign_key): Foreign key to orders table.
- payment_sequential (identifier): Payment sequence number.
- payment_type (categorical): Payment method used by customer.
- payment_installments (metric): Number of installments.
- payment_value (metric): Total payment amount.

### Table: order_reviews
Description: Customer review and satisfaction information.
Business rules:
- review_score ranges from 1 to 5.
Columns:
- review_id (identifier): Review identifier; unique together with order_id.
- order_id (foreign_key): Foreign key to orders table.
- review_score (metric): Customer satisfaction score from 1 to 5.
- review_comment_title (text): Review title.
- review_comment_message (text): Review text message.
- review_creation_date (timestamp): Review creation timestamp.
- review_answer_timestamp (timestamp): Timestamp when review was answered.

### Table: products
Description: Product metadata and physical dimensions.
Business rules:
- Product names are not available.
- Use translated category names for business-friendly output.
Columns:
- product_id (identifier): Unique product identifier.
- product_category_name (categorical): Product category in Portuguese.
- product_name_lenght (metric): Length of product name text.
- product_description_lenght (metric): Length of product description.
- product_photos_qty (metric): Number of product photos.
- product_weight_g (metric): Product weight in grams.
- product_length_cm (metric): Product length in centimeters.
- product_height_cm (metric): Product height in centimeters.
- product_width_cm (metric): Product width in centimeters.

### Table: sellers
Description: Seller identity and location information.
Columns:
- seller_id (identifier): Unique seller identifier.
- seller_zip_code_prefix (location): Seller ZIP code prefix.
- seller_city (location): Seller city.
- seller_state (location): Seller state abbreviation.

### Table: geolocation
Description: ZIP code geolocation mapping.
Columns:
- geolocation_zip_code_prefix (location): ZIP code prefix.
- geolocation_lat (coordinate): Latitude coordinate.
- geolocation_lng (coordinate): Longitude coordinate.
- geolocation_city (location): City name.
- geolocation_state (location): State abbreviation.

### Table: product_category_name_translation
Description: Translation mapping for product categories.
Business rules:
- Prefer English category names for business-facing outputs.
Columns:
- product_category_name (categorical): Portuguese category name.
- product_category_name_english (categorical): English-translated category name.

## Global business rules
- Try to find business-friendly aggregation levels for metrics.
- For most analytical questions, prefer gold.order_item_facts because it is the primary AI analytics serving table.
- Use gold aggregate marts only when the question directly asks for a pre-aggregated view such as monthly, category, seller, state, payment, or delivery performance.
- Use silver tables for validation, data quality, or normalized warehouse questions.
- try to find names instead of IDs when possible.
- if there is names, return just the names instead of the IDs. except explicitly requested to return the IDs.
- always return product category names instead of IDs, using the translation table when possible.
- never return raw identifiers like product_id or seller_id unless explicitly requested.
- Prefer translated English category names when available.
- Use customer_unique_id for repeat customer analysis.
- Avoid returning raw identifiers unless explicitly requested.
- Prefer business-friendly aggregation levels.
