# AI Business Analyst

An experimental AI analytics platform that connects Large Language Models with a PostgreSQL/Supabase warehouse using natural language business questions.

Repository: [rafli-1729/ai-business-analyst](https://github.com/rafli-1729/ai-business-analyst?utm_source=chatgpt.com)
Live Demo: [AI Business Analyst Demo](https://ai-business-analyst-k5bx.vercel.app/?utm_source=chatgpt.com)

This project was built mainly to learn and experiment with how AI systems can safely communicate with databases for analytical workloads.

The system allows users to ask business questions in natural language, then automatically generates analytical SQL queries using an LLM through OpenRouter, executes them against a Supabase/PostgreSQL warehouse, and returns summaries and query results through a lightweight web interface.

---

# Main Flow

```text id="e3vjlwm"
User Question
  -> Next.js Frontend
  -> FastAPI Backend
  -> OpenRouter LLM
  -> SQL Generation
  -> SQL Validation
  -> Supabase/PostgreSQL
  -> Query Result + Summary
```

Example:

```text id="n05m1w"
"Which product categories generate the highest revenue?"
```

The backend sends the question to an LLM through OpenRouter, the LLM generates SQL, then the query is validated before being executed against the warehouse.

The result is returned back to the frontend together with generated SQL, summaries, and execution metadata.

---

# Main Goals

The main focus of this project is learning and experimentation around:

* AI-to-database integration
* Natural language to SQL systems
* Safe LLM database access
* Warehouse architecture
* Analytical orchestration
* Semantic metadata for LLM context
* Data engineering workflows
* Understanding how modern AI analytics systems work internally

This repository is intentionally more focused on backend architecture and warehouse flow rather than frontend polish.

---

# Data Warehouse Architecture

The warehouse follows a medallion-style architecture.

```text id="1j7aj1"
Raw Data Sources
  -> Bronze
  -> Silver
  -> Gold
  -> Semantic Layer
  -> AI Query Layer
```

Additional schemas are also used:

* `reference`
* `ops`

Current schema responsibilities:

### Bronze

Raw ingested data with minimal modification.

### Silver

Cleaned and standardized warehouse entities.

### Gold

Analytics-ready marts and aggregated business tables.

The movement from Bronze → Silver → Gold depends heavily on data quality and transformation readiness.

### Reference

Contains relatively static supporting datasets such as:

* geolocation data
* calendar tables
* supporting lookup tables

### Ops

Operational metadata and logging schema.

Used for:

* ingestion tracking
* checksums
* pipeline metadata
* ingestion logs
* operational observability

---

# Ingestion and Transformation Philosophy

The ingestion layer and transformation layer are intentionally separated.

### Ingestion

The ingestion pipeline is only responsible for:

* fetching data
* loading raw data
* inserting data into PostgreSQL

No heavy transformation is done during ingestion.

### Transformation

Transformations are executed directly inside PostgreSQL.

This design was chosen to simulate real-world large-scale warehouse conditions where:

* data volume becomes very large
* transformations are pushed into the database engine
* compute power comes from the warehouse itself instead of Python memory

So instead of:

```text id="ks2s1d"
Python transforms everything locally
```

the project tries to follow:

```text id="9x8t13"
Python ingests data
Database transforms data
```

which is closer to how modern analytical warehouses usually operate.

---

# Data Sources

The current warehouse uses multiple data sources:

* Kaggle datasets
* Google Sheets

The ingestion system is registry-driven.

Configuration can be seen in:

```text id="x70vkf"
warehouse/registry.py
```

New datasets can be added by:

1. registering them in the registry
2. adjusting the ingestor/source configuration

The ingestion pipeline dynamically resolves:

* source type
* schema routing
* ingestion behavior

instead of hardcoding every dataset manually.

---

# Security and Database Access Separation

One important design choice in this project is separating database permissions between ingestion systems and AI systems.

### Ingestion Role

The ingestion pipeline has permissions for:

* INSERT
* CREATE
* warehouse transformation workflows

because its responsibility is maintaining the warehouse.

### LLM Role

The LLM only has read/query access.

It cannot:

* modify tables
* delete records
* update schemas
* directly mutate the warehouse

This separation exists to reduce risk from unsafe SQL generation or LLM hallucination.

The AI can analyze the warehouse, but it cannot directly modify it.

---

# AI Orchestration

The repository already includes an early orchestration layer for analytical reasoning.

Current flow includes:

* query planning
* SQL generation
* SQL validation
* execution flow
* response summarization
* lightweight multi-step reasoning

Some analytical “agent-like” behaviors already exist, but most of them are still relatively hardcoded and experimental.

The system is still evolving and not fully autonomous.

---

# Tech Stack

* FastAPI
* Next.js
* Supabase/PostgreSQL
* OpenRouter API
* SQLAlchemy
* pandas
* Dagster
* dbt-core

---

# Dagster Plan (Almost Happened)

The original plan was to integrate the warehouse orchestration more deeply with Dagster.

The idea was:

* orchestrated ingestion
* lineage tracking
* simulated streaming data pipelines
* scheduled warehouse updates

The project originally aimed to simulate streaming-like warehouse ingestion behavior.

But unfortunately the AI agent credits ran out halfway through development

So the Dagster integration currently exists more as an early scaffold instead of a fully operational orchestration system.

---

# Current Limitations

This project is still experimental and has many limitations.

### Dataset Quality

The warehouse data is still not fully cleaned because the main goal of the project is learning AI/database integration rather than building a perfect analytics warehouse.

### LLM Reliability

Most queries currently use fully free LLM models through OpenRouter.

Because of this:

* invalid SQL can still happen
* hallucinated queries can still happen
* model behavior can be inconsistent
* response quality may vary

Some orchestration and “agent-ish” logic is also still hardcoded.

Sometimes the free model endpoint itself may fail or disappear.

There is currently no model selector yet, so if the selected free model becomes unavailable or unstable, the system may temporarily fail.

So if the demo suddenly breaks because the free model server exploded somewhere… sorry 😭

---

# Current Features

* Natural language analytics queries
* AI-generated PostgreSQL queries
* SQL safety validation
* Supabase warehouse execution
* Bronze/Silver/Gold warehouse layers
* Reference and operational schemas
* Semantic metadata for LLM context
* Basic orchestration and reasoning flow
* Response caching
* Query execution metadata
* Lightweight analytics UI

---

# Development

Run backend:

```bash id="xf9x6g"
uvicorn apps.api.main:app --reload
```

Run frontend:

```bash id="rzz8i4"
cd apps/ui
npm install
npm run dev
```

Run ingestion and transformation:

```bash id="07pw0w"
python orchestration/pipelines/ingestion_pipelines.py
python orchestration/pipelines/transformation_pipelines.py
```

---

# Additional Notes

This project was built using:

* Codex Free Plan
* Haiku VSCode integrated AI agent

The frontend UI is intentionally simple because the repository mainly exists as:

* a learning project
* an architecture experiment
* a demonstration of AI + database integration systems
