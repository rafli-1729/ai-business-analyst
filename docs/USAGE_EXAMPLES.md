"""
Usage Examples for AI Analytics Platform

> **IMPORTANT NOTE:** These examples mostly describe the **target architecture** (ai/ package). 
> The current active implementation uses the `core_analytics/` package.
> See the end of this document for current usage examples.

# BASIC QUERY EXECUTION

"""

# Example 1: Using the new orchestrator directly

from infra.config.settings import get_settings
from ai.orchestrators.analytical_orchestrator import AnalyticalOrchestrator

settings = get_settings()
orchestrator = AnalyticalOrchestrator(settings)

# Execute a simple query

result = orchestrator.execute_query(
question="What is our total revenue by month?",
row_limit=100,
)

# Access results

print(f"SQL: {result.sql}")
print(f"Rows: {result.dataframe.head()}")
print(f"Summary: {result.summary}")
print(f"Active Agents: {result.active_agents}")

# Example 2: Using agents directly

from ai.agents.sales_agent import SalesAgent
from ai.agents.geography_agent import GeographyAgent

sales_agent = SalesAgent()
print(f"Agent: {sales_agent.name}")
print(f"Primary Mart: {sales_agent.primary_mart}")
print(f"Focus: {sales_agent.analytical_focus}")

context = sales_agent.build_analytical_context(
question="Revenue by region?",
mart="sales",
)

# Example 3: Using the agent registry

from ai.agents.initialization import initialize_agents
from ai.registries.agent_registry import get_agent

initialize_agents()

sales = get_agent("sales")
trend = get_agent("trend")
geographic = get_agent("geography")

print(f"Sales Agent: {sales.name}")
print(f"Trend Agent: {trend.name}")
print(f"Geography Agent: {geographic.name}")

# Example 4: Services in isolation

from ai.providers.schema_context_provider import SchemaContextProvider
from ai.validators.sql_validator import SqlValidator
from ai.services.prompt_composer import PromptComposer
from ai.services.sql_repair_service import SqlRepairService
from ai.services.llm import LlmClient

# Create components

schema_provider = SchemaContextProvider()
prompt_composer = PromptComposer(schema_provider)
validator = SqlValidator()

# Use services

schema = schema_provider.render_for_prompt("revenue by month")
prompt = prompt_composer.build_sql_generation_prompt(
question="Revenue by month?",
context={"intent": "analysis"},
)

# Validate SQL

try:
clean_sql = validator.validate_read_only("SELECT \* FROM orders;")
print(f"Valid SQL: {clean_sql}")
except Exception as e:
print(f"Invalid SQL: {e}")

# Example 5: Response formatting

from ai.services.response_formatter_service import ResponseFormatterService
from ai.services.summarization_service import SummarizationService
import pandas as pd

formatter = ResponseFormatterService()

# Convert DataFrame to rows

df = pd.DataFrame({
"month": ["Jan", "Feb", "Mar"],
"revenue": [1000, 1500, 1200],
})

rows = formatter.dataframe_to_rows(df, limit=100)
chart_type = formatter.infer_chart_type(df)
is_truncated = formatter.is_truncated(df, row_limit=100)

print(f"Rows: {rows}")
print(f"Chart Type: {chart_type}")
print(f"Truncated: {is_truncated}")

# Example 6: MIGRATION - Old QueryService to New Orchestrator

"""
OLD CODE (QueryService):
from ai.services.query_service import QueryService
service = QueryService(settings)
sql, df = service.ask(question)

NEW CODE (Orchestrator):
from ai.orchestrators.analytical_orchestrator import AnalyticalOrchestrator
orchestrator = AnalyticalOrchestrator(settings)
result = orchestrator.execute_query(question)
sql, df = result.sql, result.dataframe

KEY DIFFERENCES:

- Old: ask() returns tuple (sql, df)
- New: execute_query() returns ExecutionResult object
- New: More metadata available (cache_hit, summary, etc.)
- New: Clearer separation of concerns
- New: Better for testing and extension
  """

# Example 7: Adding a new agent

from ai.agents.base.analytical_agent import AnalyticalAgent
from ai.registries.agent_registry import register_agent

class ProductAgent(AnalyticalAgent):
@property
def name(self) -> str:
return "product"

    @property
    def primary_mart(self) -> str:
        return "products"

    @property
    def analytical_focus(self) -> list[str]:
        return [
            "product_performance",
            "category_trends",
            "product_rankings",
        ]

    def build_system_prompt(self) -> str:
        return """

You are a product analytics expert.

Focus on:

- Product performance metrics
- Category trends
- Product rankings and performance

Generate SQL for product-specific analysis.
""".strip()

# Register the new agent

register_agent(ProductAgent)

# Now available in registry

product_agent = get_agent("product")

# Example 8: Testing components

import unittest
from unittest.mock import Mock, patch

class TestOrchestrator(unittest.TestCase):
def test_execute_query(self): # Mock dependencies
settings = Mock()
settings.openrouter_base_url = "http://mock"
settings.openrouter_api_key = "mock"
settings.llm_model = "mock"
settings.llm_timeout_s = 30
settings.llm_max_retries = 2
settings.llm_temperature = 0
settings.llm_max_tokens = 1000
settings.database_url = "mock://db"
settings.sql_cache_ttl_s = 3600
settings.response_cache_ttl_s = 900
settings.max_question_chars = 1000
settings.summary_max_tokens = 500
settings.debug = False

        # Create orchestrator with mocked dependencies
        with patch('ai.orchestrators.analytical_orchestrator.LlmClient'):
            with patch('ai.orchestrators.analytical_orchestrator.SqlExecutor'):
                orchestrator = AnalyticalOrchestrator(settings)

        # Test would continue with mocked calls...

# Example 9: Models usage

from ai.models.analytical_context import AnalyticalContext
from ai.models.execution_result import ExecutionResult
from ai.models.query_plan import QueryPlan, QueryTask

# Create context

context = AnalyticalContext(
intent="trend_analysis",
agent="trend",
mart="sales",
question="Revenue trends?",
refresh=False,
row_limit=100,
focus_areas=["temporal_trends", "seasonality"],
)

# Convert to dict for passing around

context_dict = context.to_dict()

# Create query plan

task = QueryTask(
question="What's the trend?",
agent="trend",
mart="sales",
intent="trend_analysis",
order=1,
)

plan = QueryPlan(
intent="trend_analysis",
requires_reasoning=False,
agent="trend",
mart="sales",
tasks=[task],
)

plan_dict = plan.to_dict()

# Example 10: Dependency Injection in FastAPI

"""
In apps/api/dependencies/settings.py:

    @lru_cache(maxsize=1)
    def get_orchestrator() -> AnalyticalOrchestrator:
        return AnalyticalOrchestrator(get_settings())

In apps/api/routes/query.py:

    @router.post("/query")
    def run_query(
        payload: QueryRequest,
        orchestrator: AnalyticalOrchestrator = Depends(get_orchestrator),
    ):
        result = orchestrator.execute_query(
            question=payload.question,
            row_limit=payload.row_limit,
        )
        return format_response(result)

"""
