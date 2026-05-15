# Warehouse Architecture

## Target Flow

```text
Bronze source tables
  -> raw compatibility views
  -> Silver normalized warehouse
  -> Gold order_item_facts
  -> Gold aggregate marts
  -> LLM / Dashboard / API
```

## Project Structure

```text
ingestion/              Dataset discovery, checksums, metadata, bronze loading
warehouse/              Schema bootstrap and ordered SQL ELT execution
quality/                Quality issue summary helpers
feature_engineering/    Feature catalog for gold.order_item_facts
orchestration/          End-to-end ingestion and ELT pipeline
models/                 Pipeline dataclasses
utils/                  Shared SQL identifier helpers
sql/bronze/             Raw compatibility views and warehouse helper functions
sql/silver/             Clean normalized warehouse tables and quality issues
sql/gold/               Wide serving fact table and aggregate marts
```

## Bronze

Bronze preserves source-aligned Olist CSV tables in the `bronze` schema. Ingestion adds only operational metadata:

- `_ingested_at`
- `_source_file`
- `_source_checksum`
- `_ingestion_run_id`

The `raw` schema is a compatibility layer that exposes source columns without ingestion metadata. This keeps downstream SQL stable while preserving immutable ingestion metadata in Bronze.

## Silver

Silver is the clean normalized warehouse. It standardizes datatypes, deduplicates canonical entities, validates relationships, normalizes geolocation to one deterministic row per ZIP prefix, and materializes issues in `silver.data_quality_issues`.

Core tables:

- `silver.customers`
- `silver.orders`
- `silver.order_items`
- `silver.order_payments`
- `silver.order_reviews`
- `silver.products`
- `silver.sellers`
- `silver.geolocation_zip_prefixes`
- `silver.product_category_name_translation`

## Gold Serving Layer

`gold.order_item_facts` is the primary serving table for LLM and dashboard analytics. It has one row per order item and denormalizes high-value business semantics to reduce join load.

Feature groups:

- Delivery/logistics: distance, delivery days, delay, processing, handling, efficiency, late delivery flags
- Customer behavior: total orders, total spent, average order value, lifetime, frequency, recency, RFM-like scores
- Seller intelligence: revenue, orders, unique customers, average review, late delivery rate, revenue rank
- Product intelligence: average review, shipping cost, volume, density, return risk proxy
- Temporal: year, month, day, weekday, hour, weekend, holiday, season
- Payment: installments, payment complexity, multi-payment, payment-to-order ratio
- Geography: customer/seller distance, urban proxy, regional difficulty

## Aggregate Marts

Aggregate marts are secondary and derive only from `gold.order_item_facts`:

- `gold.sales_summary`
- `gold.category_performance`
- `gold.state_performance`
- `gold.seller_performance`
- `gold.payment_method_performance`
- `gold.delivery_performance`

## Indexing Strategy

Silver indexes optimize deterministic joins:

- entity keys: `customer_id`, `order_id`, `product_id`, `seller_id`
- join keys: order/customer/product/seller references
- geolocation ZIP prefix
- order purchase timestamp
- quality issue type

Gold indexes optimize LLM-generated filters and dashboard slicing:

- `order_id`
- `customer_unique_id`
- `seller_id`
- `product_id`
- `product_category_name`
- `purchase_month_start_date`
- `customer_state`
- `seller_revenue_rank`
- descending `order_item_revenue`

## Orchestration

`python ingest.py` runs:

1. Bootstrap base schemas
2. Load Bronze tables from Kaggle CSVs
3. Record ingestion metadata in `ops.ingestion_runs`
4. Optionally run downstream ELT

`python transform.py` runs only the database ELT:

1. `sql/bronze`
2. `sql/silver`
3. `sql/gold`
4. Record ELT metadata in `ops.elt_runs`
