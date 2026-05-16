"""
AI Analytics Platform - Refactored Architecture

# OVERVIEW

Transformed from a monolithic text-to-SQL backend into a scalable
agentic analytics orchestration platform with clear separation of concerns.

# ARCHITECTURAL PRINCIPLES

1. SEMANTIC BOUNDARIES
   - Each component has a single, well-defined responsibility
   - Clear interfaces between components
   - Minimal coupling, maximum cohesion

2. SCALABILITY FOUNDATION
   - Agent-based architecture supports new analytical agents
   - Registry pattern enables dynamic agent registration
   - Service-oriented design allows independent service scaling
   - Modular prompting supports agent specialization

3. OBSERVABILITY PRESERVATION
   - Request tracking through IDs
   - Timing metrics at each phase
   - Event logging at decision points
   - Cache behavior visibility

4. TYPE SAFETY
   - Typed models for all data structures
   - Dataclasses for clarity and immutability
   - Optional typing for flexibility

# COMPONENT HIERARCHY

API LAYER (apps/api/)
├── routes/query.py
│ └── Thin endpoint that calls orchestrator
├── dependencies/settings.py
│ └── Dependency injection for orchestrator
└── schemas/
├── QueryRequest
└── QueryResponse

ORCHESTRATION (ai/orchestrators/)
└── AnalyticalOrchestrator
└── Coordinates all query workflow phases - Manages request lifecycle - Orchestrates component interactions - Handles caching at response level - No direct business logic

PROVIDERS (ai/providers/)
└── SchemaContextProvider
└── Manages schema metadata - Loads schema context - Provides versioning - Renders schema for prompts - No SQL generation

PLANNERS (ai/planners/) [EXISTING - TO BE REFACTORED]
├── intent_classifier.py
├── mart_selector.py
├── agent_router.py
├── query_decomposer.py
└── semantic_planner.py
└── Decomposes queries into execution plans - Classifies user intent - Selects appropriate marts - Routes to agents - Plans multi-step tasks

AGENTS (ai/agents/)
├── base/analytical_agent.py
│ └── AnalyticalAgent (abstract base)
│ - Defines agent contract
│ - Provides context building
│ - Houses prompting strategy
├── diagnostic_agent.py
├── trend_agent.py
├── ranker_agent.py
├── sales_agent.py
├── geography_agent.py
├── customer_agent.py
├── retention_agent.py
├── operations_agent.py
└── initialization.py
└── Registers agents at startup

REGISTRIES (ai/registries/)
└── agent_registry.py
└── Manages agent lifecycle - Registry pattern (no giant if/else) - Dynamic agent selection - Agent instance caching - Pattern-based lookup

SERVICES (ai/services/)
├── llm.py [EXISTING]
│ └── LLM communication
├── schema_loader.py [EXISTING]
│ └── Schema file loading
├── sql_guard.py [EXISTING]
│ └── SQL parsing and extraction
├── result_formatter.py [EXISTING]
│ └── DataFrame formatting
├── prompt_composer.py [NEW]
│ └── Modular prompt building
│ - Constructs SQL generation prompts
│ - Builds repair prompts
│ - Injects context
├── sql_repair_service.py [NEW]
│ └── SQL validation and repair
│ - Validates SQL
│ - Generates repair prompts
│ - Handles repair retries
├── response_formatter_service.py [NEW]
│ └── Result formatting orchestration
│ - Converts DataFrames to rows
│ - Infers chart types
│ - Detects truncation
└── summarization_service.py [NEW]
└── Result summarization - Generates narrative summaries - Manages summary versioning - Caches prompt fingerprints

VALIDATORS (ai/validators/)
└── sql_validator.py
└── SQL validation logic - Wraps sql_guard - Provides consistent interface - Read-only enforcement

EXECUTORS (ai/executors/)
└── sql_executor.py
└── SQL execution - Wraps DatabaseExecutor - Timing collection - Result retrieval

MODELS (ai/models/)
├── analytical_context.py
│ └── AnalyticalContext
│ - Intent, agent, mart, question
│ - Focus areas, metadata
├── execution_result.py
│ └── ExecutionResult
│ - Complete query execution state
│ - SQL, DataFrame, summary
│ - Timings, cache status
├── query_plan.py
│ ├── QueryPlan
│ │ - Execution strategy
│ │ - Multi-step tasks
│ └── QueryTask
│ - Individual decomposed task

CACHES (ai/caches/) [EXISTING]
├── sql_cache.py
│ └── Caches generated SQL by question
├── response_cache.py
│ └── Caches complete responses
│ - Handles versioning
│ - TTL management

PROMPTS (ai/prompts/)
├── [Existing files - to be reorganized]
├── analytical.txt
├── decomposition.txt
├── planning.txt
└── summarization.txt
[Future modular structure:]
├── base/
│ ├── sql_system.txt
│ ├── sql_rules.txt
│ └── reasoning_system.txt
├── agents/
│ ├── sales_agent.txt
│ ├── geography_agent.txt
│ ├── customer_agent.txt
│ ├── retention_agent.txt
│ └── operations_agent.txt
├── planners/
│ └── decomposition_planner.txt
└── summarizers/
└── narrative_summary.txt

# WORKFLOW PHASES

1. REQUEST ENTRY (API Layer)
   - QueryRequest received
   - Orchestrator retrieved via DI
   - Response cache checked
     → QueryResponse returned if cached

2. SQL GENERATION PHASE (Orchestrator)
   - Check SQL cache
   - Build generation prompt via PromptComposer
   - Call LLM
   - Repair via SqlRepairService if needed
   - Cache SQL

3. EXECUTION PHASE (Orchestrator)
   - Execute SQL via SqlExecutor
   - Get DataFrame result

4. FORMATTING PHASE (Orchestrator)
   - Convert DataFrame to rows via ResponseFormatterService
   - Infer chart type
   - Detect truncation

5. SUMMARIZATION PHASE (Orchestrator)
   - Generate summary via SummarizationService
   - Add metadata

6. RESPONSE CACHING (Orchestrator)
   - Cache complete response

7. RESPONSE RETURN (API Layer)
   - Format QueryResponse
   - Return to client

# KEY DESIGN PATTERNS

1. DEPENDENCY INJECTION
   - Uses FastAPI Depends
   - Orchestrator provided via get_orchestrator()
   - ResponseCache provided via get_response_cache()

2. REGISTRY PATTERN
   - AgentRegistry for dynamic agent selection
   - Avoids giant if/else branches
   - Enables plugin architecture

3. DATACLASS MODELS
   - AnalyticalContext, ExecutionResult, QueryPlan
   - Type safety without ORM overhead
   - Clear data contracts

4. SERVICE LAYER
   - PromptComposer encapsulates prompt building
   - SqlRepairService encapsulates validation/repair
   - ResponseFormatterService encapsulates formatting
   - SummarizationService encapsulates summarization

5. PROVIDER PATTERN
   - SchemaContextProvider manages schema lifecycle
   - Single source of truth for schema
   - Centralized schema versioning

6. EXECUTOR PATTERN
   - SqlExecutor handles database side effects
   - Isolated database coupling
   - Timing collection at execution

# SEPARATION OF CONCERNS

ORCHESTRATOR RESPONSIBILITIES:
✓ Workflow coordination
✓ Component sequencing
✓ Timing collection
✓ Request lifecycle management
✗ SQL generation
✗ Database access
✗ Business logic

AGENT RESPONSIBILITIES:
✓ Specialized prompting
✓ Context building
✓ Analytical focus definition
✗ SQL execution
✗ Database connection
✗ Orchestration

SERVICE RESPONSIBILITIES:
✓ Single capability
✓ Reusable logic
✓ No state management
✗ Workflow coordination

VALIDATOR RESPONSIBILITIES:
✓ Validation rules
✓ Safety checking
✗ Repair logic (delegated to SqlRepairService)

EXECUTOR RESPONSIBILITIES:
✓ Side effects (SQL execution)
✓ Result retrieval
✗ Validation
✗ Caching

# MIGRATION PATH

PHASE 1: NEW ARCHITECTURE IN PLACE (Current)

- New components created and integrated
- API layer updated to use orchestrator
- All imports validated
- Old QueryService still exists but unused

PHASE 2: MULTI-STEP REASONING REFACTOR

- Update analytical_flow.py to use orchestrator
- Refactor planner integration
- Update agent invocation for multi-step flows
- Test multi-agent reasoning

PHASE 3: PROMPT MODULARIZATION

- Organize prompts into structured directories
- Create agent-specific prompt files
- Implement prompt composition
- Externalize all hard-coded prompts

PHASE 4: LEGACY ADAPTER

- Create QueryService adapter (for backward compatibility if needed)
- Redirect old imports to new architecture
- Deprecation warnings
- Plan removal timeline

PHASE 5: CLEANUP

- Remove old orchestration/analytical_flow.py
- Remove all god-object patterns
- Remove scattered logic
- Full test coverage of new architecture

# ADVANTAGES OF NEW ARCHITECTURE

SCALABILITY:

- Easy to add new specialized agents
- Service-oriented design allows independent scaling
- Provider pattern centralizes context management
- Registry pattern enables dynamic extension

MAINTAINABILITY:

- Clear semantic boundaries
- Single responsibility per component
- Dependency injection for testing
- Type safety throughout

OBSERVABILITY:

- Request tracking preserved
- Timing metrics at each phase
- Event logging preserved
- Cache behavior visible

TESTABILITY:

- Models provide clear test fixtures
- Dependency injection enables mocking
- Service layer enables unit testing
- Orchestrator enables integration testing

EXTENSIBILITY:

- New agents can be added by extending AnalyticalAgent
- New services can be added without changing orchestrator
- Provider pattern allows context injection
- Registry pattern enables plugin architecture

# FUTURE CAPABILITIES

With this architecture, easy to add:

- Semantic decomposition workflows
- Multi-agent collaboration
- Insight generation pipeline
- Forecasting workflows
- Anomaly detection workflows
- Recommendation engines
- Real-time streaming analytics
- A/B testing analytics
- Cohort analysis workflows
  """
