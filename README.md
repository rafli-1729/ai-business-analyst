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

### Natural Language to SQL

Users can ask business questions such as:
- "Top product categories by revenue"
- "Monthly revenue growth trend"
- "States with the highest number of orders"

The LLM automatically generates PostgreSQL queries.

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