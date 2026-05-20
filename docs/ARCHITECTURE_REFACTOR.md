AI Analytics Platform - Refactored Architecture

# OVERVIEW

Transformed from a bounded, multi-agent orchestrator with a static semantic layer into a single, highly autonomous ReAct (Reasoning and Acting) agent. This agent leverages live database schema introspection to dynamically answer queries without relying on rigid, pre-defined semantics.

# ARCHITECTURAL PRINCIPLES

1. SINGLE AUTONOMOUS AGENT
   - A singular Analyst Agent handles the end-to-end analytical workflow.
   - The agent operates in a continuous ReAct loop: Observe -> Think -> Act -> Repeat.
   - Replaces the fragmented domain-specific multi-agent swarm (`sales_agent`, `customer_agent`, etc.).

2. DATABASE AS SOURCE OF TRUTH
   - Live Schema Introspection: The agent uses tools to read table metadata instead of static YAML.
   - The database schema, keys (PKs/FKs), and indexes are discovered on the fly.
   - Sample data observation is used to understand categorical distributions dynamically.

3. STRICT READ-ONLY ENFORCEMENT
   - Direct database access is provided but strictly sandboxed.
   - The connection utilizes read-only transactions (`default_transaction_read_only=on`).
   - Query tools have built-in validation to prevent mutations and enforce `LIMIT` constraints.

4. OBSERVABILITY PRESERVATION
   - Request tracking through IDs.
   - Event logging at every step of the ReAct loop (Thought/Action/Observation).
   - Agent reasoning traces are preserved for transparency.

# COMPONENT HIERARCHY

API LAYER (apps/api/)
├── routes/query.py
│   └── Thin endpoint that invokes the autonomous agent
├── dependencies/settings.py
└── schemas/
    ├── QueryRequest
    └── QueryResponse

ANALYTICS ENGINE (core_analytics/analytics/)
├── engine.py
│   └── Orchestrates the initialization and execution of the Analyst Agent
├── tools.py
│   └── Secure Database Tooling:
│       - list_warehouse_tables
│       - describe_warehouse_table
│       - execute_analytical_query
├── sql_guard.py
│   └── Validates SQL syntax and enforces read-only operations
├── result_formatter.py
│   └── Formats tool outputs and final query results
└── summarization.py
    └── Synthesizes final insights

AGENT LAYER (core_analytics/agents/)
└── autonomous_analyst.py (NEW)
    └── Single LangChain/LlamaIndex ReAct agent
    └── Replaces: planner.py, customer_agent.py, sales_agent.py, etc.

INFRASTRUCTURE (infra/)
└── database/
    ├── engine.py
    │   └── PostgreSQL connection factory (Read-Only enabled)
    └── introspection.py
        └── Queries `information_schema` for live table structures

# WORKFLOW PHASES

1. REQUEST ENTRY
   - User submits an analytical question.

2. AUTONOMOUS REASONING LOOP (ReAct)
   - **Thought:** The agent decides what schema information is needed.
   - **Action:** Calls `list_warehouse_tables` or `describe_warehouse_table`.
   - **Observation:** Receives table metadata (columns, PKs, FKs).
   - **Thought:** Formulates a hypothesis and constructs a SQL query.
   - **Action:** Calls `execute_analytical_query` to test the hypothesis.
   - **Observation:** Reviews sample results or query errors.
   - **Correction (if needed):** If an error occurs (e.g., column not found), the agent adapts and retries.

3. ARTIFACT SYNTHESIS
   - The final successful query and results are passed to the Summarization/Visualization layer.

4. RESPONSE DELIVERY
   - Executive summary, visual charts, and reasoning traces are returned to the user.

# MIGRATION PATH

PHASE 1: ARCHITECTURE PIVOT
- Overwrite `GEMINI.md` to officially sanction the single autonomous agent pattern.
- Update `ARCHITECTURE_REFACTOR.md` to reflect the pivot.

PHASE 2: SECURE DATABASE TOOLING
- Ensure `infra/database/engine.py` uses a strictly read-only role/user.
- Implement robust introspection tools (`list_tables`, `describe_table`, `execute_query`).

PHASE 3: THE AUTONOMOUS AGENT
- Create `autonomous_analyst.py` implementing the ReAct loop.
- Integrate the agent with the existing `engine.py`.

PHASE 4: CLEANUP & DEPRECATION
- Remove deprecated domain agents (`customer_agent`, `sales_agent`, etc.).
- Remove the `Planner` agent and related orchestration logic.
- Clean up outdated static semantic artifacts.

# ADVANTAGES OF NEW ARCHITECTURE

- **Flexibility:** Dynamically adapts to schema changes without requiring manual YAML updates.
- **Resilience:** The agent automatically handles "Table Not Found" or "Column Not Found" errors by exploring alternatives.
- **Simplicity:** Removes over-engineered orchestrators and god-object patterns.
- **True Autonomy:** Empowers the LLM to behave like a real data analyst rather than a simple text-to-SQL parser.
