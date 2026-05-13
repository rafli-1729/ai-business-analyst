# Semantic Layer

The semantic layer gives the NLQ system business context that is not obvious from
database column names alone.

Current semantic inputs:

- database overview and layer descriptions
- analytics table descriptions
- column descriptions and semantic types
- business rules
- preferred table usage guidance

The active LLM context is `warehouse/semantic/semantic_context.md`. It is kept as
plain text so prompt content can be edited directly without rendering a large JSON
document through Python dictionaries.

Structural metadata that may drive PK/FK/index logic lives separately in
`warehouse/semantic/table_relations.json`. This keeps machine-readable warehouse
relationships available without mixing them into the business-facing prompt text.

The legacy monolithic schema artifact has been removed. Runtime prompt context
now comes from the text semantic context and structural relation data.

Near-term improvements:

- document high-value dimensions in `warehouse/semantic/dimensions`
- capture grain and join rules in `warehouse/semantic/relationships`
- continue improving semantic scoring for relevant prompt context
