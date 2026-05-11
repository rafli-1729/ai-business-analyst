# Relational AI Analyst

An AI-powered business intelligence system that transforms natural language questions into analytical PostgreSQL queries using a relational business warehouse.

This project is designed as an intermediate AI engineering project focused on:
- relational database analytics
- semantic-aware SQL generation
- AI orchestration
- business intelligence workflows
- agentic AI foundations

---

## Project Goals

The main goal of this project is to simulate a realistic AI-powered analytics workflow used in modern business intelligence systems.

The system allows users to:
1. Ingest relational business datasets into PostgreSQL (Supabase)
2. Query relational data using natural language
3. Generate analytical SQL automatically using LLMs
4. Execute safe SQL queries
5. Return business insights interactively

This project focuses heavily on:
- relational reasoning
- schema understanding
- semantic metadata engineering
- AI-assisted analytics
- system orchestration

---

## Tech Stack

### Database
- Supabase PostgreSQL

### LLM Provider
- OpenRouter

### Frontend
- Streamlit

### Data Processing
- pandas
- SQLAlchemy

### Dataset
- Olist Brazilian E-Commerce Dataset

---

## Current Features

### Relational Data Warehouse

Multi-table business warehouse using:
- customers
- orders
- order_items
- order_payments
- order_reviews
- products
- sellers
- geolocation

---

### Chunked Data Ingestion

Efficient ingestion pipeline with:
- chunked CSV loading
- datetime conversion
- tqdm progress tracking
- scalable loading strategy

---

### Layered ELT Warehouse

Database-native transformations are organized for AI-powered analytics:
- `bronze`: immutable source-aligned tables with ingestion metadata
- `raw`: compatibility views over source tables with ingestion metadata hidden
- `silver`: normalized, typed, deduplicated, quality-flagged warehouse entities
- `gold.order_item_facts`: wide denormalized serving table with feature-engineered business semantics
- `gold.*_performance` marts: secondary aggregate tables derived from `gold.order_item_facts`

Recommended flow:

```bash
python ingest.py
python transform.py
```

By default, `python ingest.py` also runs the ELT layer builder after ingestion. Set `RUN_ELT_AFTER_INGEST=false` if you want to load raw data only and run `python transform.py` separately.

The ELT runner executes SQL files in this order:
- `sql/bronze`
- `sql/silver`
- `sql/gold`

Runs are recorded in `ops.elt_runs`. Formal validation findings from the preparation notebook are materialized in `silver.data_quality_issues`.

Project modules are split by responsibility:

```text
ingestion/              Bronze ingestion and source metadata
warehouse/              ELT runner and schema bootstrap
quality/                Quality issue readers and summaries
feature_engineering/    Gold feature catalog
orchestration/          End-to-end warehouse pipeline
models/                 Pipeline config/result models
utils/                  Shared SQL helpers
sql/bronze/             Bronze compatibility SQL
sql/silver/             Clean normalized warehouse SQL
sql/gold/               AI serving fact table and aggregate marts
```

`gold.order_item_facts` is the default table for LLM/text-to-SQL analytics. It minimizes joins and exposes semantic columns such as `customer_satisfaction_score`, `total_order_item_cost`, `delivery_distance_km`, `customer_rfm_score`, `seller_revenue_rank`, and `product_return_risk_proxy`.

See `docs/warehouse_architecture.md` for the detailed warehouse design, feature groups, orchestration strategy, and indexing strategy.

---

### Natural Language to SQL

Users can ask business questions such as:
- "Top product categories by revenue"
- "Monthly revenue growth trend"
- "States with the highest number of orders"

The LLM automatically generates PostgreSQL queries.

---

### Next.js UI

The deployable web UI is built with Next.js App Router and is ready for Vercel.

```bash
npm install
npm run dev
```

By default, the UI calls `/api/query`, which returns demo analytics data. Set `ANALYTICS_API_URL` in Vercel when you have a deployed backend endpoint that accepts `{ "question": "..." }` and returns `sql`, `summary`, `rows`, and `chartType`.

---

### Semantic Schema Layer

The system uses a business-aware semantic schema containing:
- table descriptions
- column descriptions
- relationship metadata
- business rules
- analytical guidance

This improves:
- SQL generation quality
- business understanding
- semantic reasoning
- aggregation behavior

---

### Relational Query Reasoning

The AI system supports:
- multi-table JOIN generation
- aggregation queries
- trend analysis
- ranking queries
- analytical KPI generation

---

### SQL Safety Guard

The system blocks dangerous SQL execution such as:
- DROP
- DELETE
- UPDATE
- ALTER
- TRUNCATE
- INSERT
- CREATE

Only analytical SELECT queries are allowed.

---

## Planned V2 Improvements

### 1. LLM Validation & Retry Loop

Implement automatic SQL repair when:
- query execution fails
- query returns empty results
- datatype mismatch occurs

---

### 2. AI Summary Layer

Generate executive-style business summaries from query results.

Example:

> "Health & Beauty products generated the highest revenue during the selected period."

---

### 3. Automatic Visualization Layer

Generate charts dynamically based on query output.

Planned visualizations:
- line charts
- bar charts
- KPI cards
- trend analysis

---

### 4. Query Observability

Track:
- generated SQL
- execution time
- query failures
- retry attempts

---

### 5. Database Optimization

Planned improvements:
- PostgreSQL COPY ingestion
- automatic index creation
- automatic foreign key creation

---

### 6. Semantic Metadata Expansion

Improve business-aware reasoning using:
- metric definitions
- semantic aliases
- aggregation preferences
- ontology-style metadata

---

### 7. Modular Architecture Refactor

Planned structure:

project/
│
├── app.py
├── ingest.py
├── schema.py
├── prompts.py
├── validator.py
│
├── utils/
│   ├── db.py
│   ├── llm.py
│   └── visualization.py

---

### 8. Better Prompt Engineering

Improve:
- semantic query understanding
- aggregation granularity
- business-friendly outputs
- human-readable query generation

---

### 9. Conversational Analytics

Enable contextual follow-up questions such as:
- "What about only in 2018?"
- "Compare it with the previous year."

---

### 10. Performance Improvements

Future optimizations:
- caching
- query optimization
- asynchronous execution
- better ingestion throughput

---

## Example Workflow

User Question
↓
LLM SQL Generation
↓
SQL Safety Validation
↓
PostgreSQL Query Execution
↓
Result Visualization
↓
AI Business Summary

---

## Example Questions

- Which states generate the highest revenue?
- What are the top product categories by sales?
- Monthly revenue growth trend
- Which payment methods have the highest average transaction value?
- Which categories have the best customer review scores?

---

## Learning Objectives

This project is intended to explore:
- relational database engineering
- AI-assisted analytics
- semantic metadata systems
- LLM orchestration
- NLQ-to-SQL systems
- business intelligence workflows
- agentic AI foundations
