# Olist Brazilian E-Commerce Warehouse

Schema version: v2

---

## gold.sales_summary

Description:
Daily business sales performance summary mart.

Layer:
gold

Grain:
One row per purchase_date.

Primary dimensions:
- purchase_date

Primary metrics:
- total_revenue
- total_orders
- total_customers
- total_items
- average_order_value
- average_freight_value

Preferred for:
- trend_analysis
- executive_summary
- growth_analysis

Columns:
- purchase_date: Purchase date at daily grain. Format: YYYY-MM-DD. Semantic type: date.
- total_revenue: Total successful payment revenue. Unit: BRL. Semantic type: metric.
- total_orders: Total distinct orders. Semantic type: metric.
- total_customers: Total unique customers. Semantic type: metric.
- total_items: Total items sold. Semantic type: metric.
- average_order_value: Average payment value per order. Unit: BRL. Semantic type: metric.
- average_freight_value: Average freight cost per item. Unit: BRL. Semantic type: metric.

---

## gold.category_sales

Description:
Daily category-level sales performance mart.

Layer:
gold

Grain:
One row per purchase_date and product_category.

Primary dimensions:
- purchase_date
- product_category

Primary metrics:
- total_revenue
- total_orders
- total_items
- average_review_score

Preferred for:
- ranking_analysis
- category_analysis
- product_performance

Columns:
- purchase_date: Purchase date. Format: YYYY-MM-DD. Semantic type: date.
- product_category: English-translated product category. Semantic type: dimension.
- total_revenue: Total revenue. Unit: BRL. Semantic type: metric.
- total_orders: Total distinct orders. Semantic type: metric.
- total_items: Total items sold. Semantic type: metric.
- average_review_score: Average customer review score. Range: 1-5. Semantic type: metric.

---

## gold.customer_metrics

Description:
Customer-level purchasing and revenue behavior mart.

Layer:
gold

Grain:
One row per customer_unique_id.

Primary dimensions:
- customer_unique_id
- customer_state

Primary metrics:
- total_orders
- total_revenue
- average_order_value

Preferred for:
- customer_analysis
- retention_analysis
- ltv_analysis

Columns:
- customer_unique_id: Persistent customer business identifier. Semantic type: business_identifier.
- customer_state: Brazilian customer state abbreviation. Semantic type: location.
- total_orders: Total distinct customer orders. Semantic type: metric.
- total_revenue: Total customer revenue contribution. Unit: BRL. Semantic type: metric.
- average_order_value: Average customer order value. Unit: BRL. Semantic type: metric.
- first_purchase_timestamp: First recorded customer purchase timestamp. Format: YYYY-MM-DD HH24:MI:SS. Semantic type: timestamp.
- latest_purchase_timestamp: Latest recorded customer purchase timestamp. Format: YYYY-MM-DD HH24:MI:SS. Semantic type: timestamp.

---

## gold.seller_performance

Description:
Seller-level sales and operational performance mart.

Layer:
gold

Grain:
One row per seller_id.

Primary dimensions:
- seller_id
- seller_state

Primary metrics:
- total_orders
- total_revenue
- average_review_score
- average_delivery_days

Preferred for:
- seller_analysis
- logistics_analysis
- operational_analysis

Columns:
- seller_id: Seller business identifier. Semantic type: business_identifier.
- seller_state: Seller Brazilian state abbreviation. Semantic type: location.
- total_orders: Total seller orders. Semantic type: metric.
- total_revenue: Total seller revenue contribution. Unit: BRL. Semantic type: metric.
- average_review_score: Average seller review score. Range: 1-5. Semantic type: metric.
- average_delivery_days: Average delivery duration in days. Unit: days. Semantic type: metric.

---

## gold.delivery_metrics

Description:
Daily logistics and delivery efficiency mart.

Layer:
gold

Grain:
One row per purchase_date.

Primary dimensions:
- purchase_date

Primary metrics:
- average_delivery_days
- late_delivery_rate

Preferred for:
- delivery_analysis
- logistics_analysis
- trend_analysis

Columns:
- purchase_date: Purchase date. Format: YYYY-MM-DD. Semantic type: date.
- average_delivery_days: Average delivery duration. Unit: days. Semantic type: metric.
- late_delivery_rate: Share of late deliveries. Range: 0.0-1.0. Semantic type: metric.

---

## gold.review_summary

Description:
Daily customer review and satisfaction mart.

Layer:
gold

Grain:
One row per purchase_date.

Primary dimensions:
- purchase_date

Primary metrics:
- average_review_score
- total_reviews
- negative_review_rate

Preferred for:
- review_analysis
- customer_satisfaction
- diagnostic_analysis

Columns:
- purchase_date: Purchase date. Format: YYYY-MM-DD. Semantic type: date.
- average_review_score: Average review score. Range: 1-5. Semantic type: metric.
- total_reviews: Total submitted reviews. Semantic type: metric.
- negative_review_rate: Share of negative reviews. Range: 0.0-1.0. Semantic type: metric.

---

## gold.payment_analysis

Description:
Daily payment behavior and payment method mart.

Layer:
gold

Grain:
One row per purchase_date and payment_type.

Primary dimensions:
- purchase_date
- payment_type

Primary metrics:
- total_payments
- total_payment_value
- average_installments

Preferred for:
- payment_analysis
- financial_analysis
- behavior_analysis

Columns:
- purchase_date: Purchase date. Format: YYYY-MM-DD. Semantic type: date.
- payment_type: Customer payment method. Semantic type: categorical.
- total_payments: Total payment transactions. Semantic type: metric.
- total_payment_value: Total payment value. Unit: BRL. Semantic type: metric.
- average_installments: Average payment installments. Semantic type: metric.

---

## gold.geographic_sales

Description:
Daily geographic sales and customer distribution mart.

Layer:
gold

Grain:
One row per purchase_date, customer_state, and customer_city.

Primary dimensions:
- purchase_date
- customer_state
- customer_city

Primary metrics:
- total_revenue
- total_orders
- total_customers

Preferred for:
- geographic_analysis
- regional_analysis
- location_analysis

Columns:
- purchase_date: Purchase date. Format: YYYY-MM-DD. Semantic type: date.
- customer_state: Customer Brazilian state abbreviation. Semantic type: location.
- customer_city: Customer city. Semantic type: location.
- total_revenue: Total revenue. Unit: BRL. Semantic type: metric.
- total_orders: Total distinct orders. Semantic type: metric.
- total_customers: Total unique customers. Semantic type: metric.

---

## gold.customer_retention

Description:
Customer repeat purchase and retention mart.

Layer:
gold

Grain:
One row per customer_unique_id.

Primary dimensions:
- customer_unique_id

Primary metrics:
- total_orders

Preferred for:
- retention_analysis
- repeat_customer_analysis
- customer_behavior

Columns:
- customer_unique_id: Persistent customer identifier. Semantic type: business_identifier.
- total_orders: Total customer orders. Semantic type: metric.
- is_repeat_customer: True if customer has more than one distinct order. Semantic type: boolean.

---

## gold.operational_efficiency

Description:
Seller operational shipping and pricing efficiency mart.

Layer:
gold

Grain:
One row per seller_id.

Primary dimensions:
- seller_id

Primary metrics:
- average_freight_value
- average_item_price
- total_items_shipped

Preferred for:
- operational_analysis
- seller_efficiency
- shipping_analysis

Columns:
- seller_id: Seller business identifier. Semantic type: business_identifier.
- average_freight_value: Average freight value. Unit: BRL. Semantic type: metric.
- average_item_price: Average item selling price. Unit: BRL. Semantic type: metric.
- total_items_shipped: Total shipped items. Semantic type: metric.