# Warehouse Workflow Summary

This architecture follows a well-structured Medallion model (Bronze, Silver, Gold), using a combination of Python scripts for ingestion and dbt projects for transformation.

---

# 1. Ingestion (Bronze Layer)

The goal of this layer is to obtain raw data copies from various sources into the warehouse.

* **Data Sources:**
  Data comes from various sources defined in `warehouse/ingestion/registry.json`:

  * Google Sheets: `customers`, `products`, `orders`, `order_items`, etc.
  * Kaggle: `geolocation`.
  * Local CSV Files: `geography_master` and `product_category_mapping`.

* **Process:**
  The ingestion process is orchestrated by Dagster. For each table, data is fetched and loaded into staging tables in PostgreSQL. From there, data is inserted into the bronze schema with adjusted data types. This creates raw but structured source data copies.

---

# 2. Transformation & Standardization (Silver Layer)

The goal of this layer is to clean, standardize, and prepare data for analysis. Transformations are performed using SQL models within the dbt project at:

```text
warehouse/transformation/models/silver/
```

## Key Standardizations Performed

* **Data Cleaning:**

  * Removing leading/trailing whitespace (using `TRIM`).
  * Converting empty strings (`''`) to `NULL` for consistency.

* **Data Type Adjustments:**

  * Ensuring all data is explicitly converted to the correct data types (e.g., `INTEGER`, `NUMERIC`, `TIMESTAMP`).

* **Value Normalization:**

  * **Geography:**
    City and state names are standardized by joining with the `master.geography_master` table to obtain canonical names.

  * **Product Category:**
    Product category names are translated to English and standardized using the `reference.product_category_mapping` table.

* **Deduplication:**

  * Duplicate data is removed from several tables (such as `customers`) based on unique keys to ensure each entity exists only once.

---

# 3. Analytical Models (Gold Layer)

This layer is the final product of the warehouse: tables ready for business analysis and reporting. These tables are "wide" (denormalized) and created by joining several tables from the silver layer.

## Tables Created in the Gold Layer

1. **`gold.fact_sales_items`**

   * Purpose: Detailed fact table, where each row represents one item in an order. This table joins order, product, seller, and customer data to enable revenue, product performance, and geographic sales analysis.

2. **`gold.fact_order_fulfillment`**

   * Purpose: Fact table focused on logistics, with one row per order. This table calculates metrics such as actual delivery time (`delivery_days_actual`) and late delivery status (`is_late_delivery`), and joins them with review data to measure customer satisfaction.

3. **`gold.mart_customer_behavior`**

   * Purpose: Customer-centric data mart, with one row per unique customer. This table calculates key metrics such as lifetime value (`LTV`), order frequency, and repeat purchase behavior.

4. **`gold.mart_monthly_performance`**

   * Purpose: High-level monthly aggregate data mart designed for executive reporting. This table tracks key metrics such as `total_revenue`, `total_orders`, and `total_customers` over time.
