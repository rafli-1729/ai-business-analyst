# AI Analytics Platform Architecture

This repository is evolving from a simple NLQ script into a small AI analytics
workspace. The design stays startup-sized: one backend, one frontend, one
warehouse, one orchestration layer.

## Runtime Flow

```text
User question
  -> Next.js analytics workspace
  -> FastAPI /api/query
  -> AI planning hints + semantic prompt
  -> OpenRouter SQL generation
  -> SQL safety validation
  -> Supabase/Postgres execution
  -> summary, rows, chart type, execution metadata
```

## Warehouse Flow

```text
Raw Olist CSV files
  -> bronze source-aligned tables
  -> silver cleaned warehouse entities
  -> gold analytics facts and marts
  -> semantic catalog
  -> AI query layer
```

## Layer Responsibilities

- `apps/api`: FastAPI contracts and routes.
- `apps/ui`: Next.js analytics workspace for prompt, SQL, results, and metadata.
- `ai`: prompt, planning, retrieval, SQL generation helpers, formatting, summaries.
- `warehouse`: ingestion, dbt transformations, semantic metadata, and quality checks.
- `orchestration`: Python pipelines and Dagster assets.
- `infra`: configuration, database, and observability adapters.
- `services`: current query, LLM, database, cache, and validation service layer used by FastAPI and local scripts.

The `services` package remains in place during the transition so existing scripts
continue to run while the target architecture is introduced incrementally.
