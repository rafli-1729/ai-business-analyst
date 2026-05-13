# AI Business Analyst

An AI analytics workspace that turns natural-language business questions into safe analytical PostgreSQL queries over a Supabase warehouse.

The project started as a simple NLQ flow:

```text
user prompt -> OpenRouter SQL generation -> Supabase query -> result display
```

It is now evolving into a practical, startup-sized AI analytics platform:

```text
User question
  -> Next.js workspace
  -> FastAPI backend
  -> AI planning + semantic prompt
  -> OpenRouter SQL generation
  -> SQL safety validation
  -> Supabase/Postgres execution
  -> table, chart intent, summary, execution metadata
```

## Goals

- Keep the system understandable for a data engineering internship evaluation.
- Separate application, AI, warehouse, orchestration, and infrastructure concerns.
- Use semantic metadata to improve NLQ-to-SQL reliability.
- Keep SQL generation read-only and analytics-focused.
- Use realistic tools without enterprise overengineering.

## Tech Stack

- Supabase/Postgres for warehouse execution
- OpenRouter for LLM calls
- FastAPI for backend API contracts
- Next.js for the analytics workspace UI
- Dagster for orchestration and asset lineage
- dbt-core for warehouse transformation structure
- pandas and SQLAlchemy for Python data access

## Project Layout

```text
apps/api/                FastAPI query API
apps/ui/                 Next.js analytics workspace
ai/                      prompts, planning, formatting, summaries
warehouse/               ingestion, dbt transformations, semantic catalog, quality
orchestration/           Python pipelines and Dagster assets
infra/                   config, database, observability adapters
services/                compatibility services used by current entry points
docs/                    architecture, lineage, semantic layer notes
sql/                     active SQL ELT files for bronze, silver, and gold
```

## Warehouse Flow

```text
Raw Olist CSV files
  -> bronze source-aligned tables
  -> raw compatibility views
  -> silver cleaned warehouse entities
  -> gold analytics facts and marts
  -> semantic catalog
  -> AI query layer
```

`gold.order_item_facts` is the default serving table for NLQ analytics. Aggregate marts support common monthly, category, seller, state, payment, and delivery questions.

## Local Commands

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example`, then run the API:

```bash
uvicorn apps.api.main:app --reload
```

Run the Next.js workspace:

```bash
cd apps/ui
npm install
npm run dev
```

For local development, keep the FastAPI backend running on port `8000`. The
Next.js API proxy defaults to `http://localhost:8000`. Use
`ANALYTICS_API_URL` only when the backend runs somewhere else. Set
`ANALYTICS_DEMO_MODE=true` only when you intentionally want mock UI data.
Set `DEBUG=true` to return and display timing breakdowns in the UI. Leave it
false to hide timing diagnostics.

Run ingestion and warehouse ELT:

```bash
python ingest.py
python transform.py
```

## API Contract

```http
POST /api/query
Content-Type: application/json

{ "question": "Which states generate the highest revenue?" }
```

The response includes:

- generated SQL
- business summary
- result rows
- chart type hint
- row count
- execution time
- schema version
- debug timing breakdown when `DEBUG=true`

## Current Capabilities

- Bronze ingestion from Olist CSV files into Supabase/Postgres
- SQL ELT for bronze compatibility views, silver warehouse tables, and gold marts
- Semantic metadata rendering for LLM prompts
- OpenRouter SQL generation
- Read-only SQL safety guard
- In-memory SQL cache
- FastAPI query endpoint
- Next.js analytics workspace shell
- Dagster asset definitions for coarse warehouse lineage
- dbt project scaffold for incremental migration from SQL scripts to dbt models

## Documentation

- `docs/architecture.md`
- `docs/warehouse_architecture.md`
- `docs/semantic_layer.md`
- `docs/lineage.md`
