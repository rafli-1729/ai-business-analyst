# Olist Brazilian E-Commerce Warehouse (Wide Marts Edition)

Schema version: v3

---

## gold.fact_sales_items

Description:
Ultimate wide table for sales and product analysis. Contains one row per item sold in every order. This is the primary table for revenue, product ranking, and geographic trends.

Layer:
gold

Grain:
One row per order_item_key (Order ID + Item ID).

Primary dimensions:
- order_id
- product_id
- product_category_name
- seller_id
- customer_id
- customer_state
- seller_state

Primary metrics:
- price
- freight_value
- total_value (Price + Freight)

Preferred for:
- revenue_analysis
- category_performance
- geographic_sales_trends
- product_ranking

Columns:
- order_item_key: Unique identifier for the item line.
- order_purchase_timestamp: When the order was placed.
- product_category_name: Normalized English category name.
- total_value: Total revenue including shipping. Semantic type: metric.
- customer_state: Buyer location. Semantic type: location.

---

## gold.fact_order_fulfillment

Description:
Logistics performance and customer satisfaction mart. Contains one row per order. Use this for delivery SLAs and review analysis.

Layer:
gold

Grain:
One row per order_id.

Primary metrics:
- delivery_days_actual
- is_late_delivery
- review_score

Preferred for:
- delivery_efficiency
- logistics_sla_analysis
- customer_satisfaction

Columns:
- order_status: Current state of the order (delivered, shipped, etc).
- delivery_days_actual: Days taken from purchase to delivery.
- is_late_delivery: Boolean flag for breached delivery estimates.
- review_score: Average customer rating (1-5).

---

## gold.mart_customer_behavior

Description:
Customer-centric mart for retention and Lifetime Value (LTV) analysis. Contains one row per unique customer.

Layer:
gold

Grain:
One row per customer_unique_id.

Primary metrics:
- total_lifetime_value
- total_orders
- is_repeat_customer

Preferred for:
- customer_retention
- segment_analysis
- ltv_calculation

Columns:
- total_lifetime_value: Sum of all purchases (price + freight) by this customer.
- is_repeat_customer: True if the customer has more than one order.

---

## gold.mart_monthly_performance

Description:
High-level monthly growth tracking. Aggregated for executive summaries.

Layer:
gold

Grain:
One row per month_start_date.

Primary metrics:
- total_revenue
- total_orders
- total_customers

Preferred for:
- mom_growth_analysis
- executive_reporting
