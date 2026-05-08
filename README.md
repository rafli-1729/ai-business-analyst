# AI Business Analyst

An AI-powered Natural Language Query (NLQ) application that allows users to ask business questions in plain English and automatically generates SQL queries to retrieve insights from a PostgreSQL database.

## Overview

This project demonstrates an end-to-end AI analytics workflow:

1. Public dataset ingestion
2. Data cleaning and preprocessing
3. PostgreSQL cloud database integration using Supabase
4. SQL query generation using LLMs via OpenRouter
5. Automated query execution
6. Interactive analytics interface using Streamlit

The application enables users to interact with structured business data without writing SQL manually.

---

## Tech Stack

* Python
* Supabase (PostgreSQL database)
* OpenRouter (LLM API gateway)
* Streamlit (web interface)
* SQLAlchemy
* Pandas

---

## Features

* Natural language to SQL conversion
* Real-time database querying
* Cloud PostgreSQL integration
* Interactive Streamlit dashboard
* Schema-aware prompting
* Dynamic business analytics workflow

---

## Example Workflow

User Question:

```text id="tjlwm4"
What are the top 5 most profitable products after 2013?
```

LLM Generated SQL:

```sql id="7jlwm5"
SELECT product_name, SUM(profit) AS total_profit
FROM sales
WHERE order_date > '2013-12-31'
GROUP BY product_name
ORDER BY total_profit DESC
LIMIT 5;
```

Result:

* Executes directly against Supabase PostgreSQL
* Returns structured business insights

---

## Project Structure

```text id="5jlwm6"
ai-business-analyst/
│
├── app.py
├── ingest.py
├── query.py
├── requirements.txt
├── .env
├── .gitignore
└── data/
    └── sales.csv
```

---

## Setup

### 1. Clone Repository

```bash id="4jlwm7"
git clone <your-repository-url>
cd ai-business-analyst
```

### 2. Install Dependencies

```bash id="6jlwm8"
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file:

```env id="3jlwm9"
SUPABASE_DB_URL=your_supabase_connection_string
OPENROUTER_API_KEY=your_openrouter_api_key
```

### 4. Run Data Ingestion

```bash id="1jlwm0"
python ingest.py
```

### 5. Start Application

```bash id="9jlwm1"
streamlit run app.py
```

---

## Future Improvements

* SQL safety validation
* Read-only database enforcement
* Conversational memory
* AI-generated business summaries
* Dynamic schema extraction
* Multi-table relational querying
* Frontend deployment with Vercel

---

## Purpose

This project was built to explore modern AI engineering workflows involving:

* AI orchestration
* LLM integration
* Data systems
* Natural language analytics
* End-to-end MVP development

It focuses on practical AI application engineering rather than model training.
