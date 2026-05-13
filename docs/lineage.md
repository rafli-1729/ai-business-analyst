# Lineage

Dagster assets model the warehouse lineage at a practical level:

```text
bronze_olist_sources
  -> silver_warehouse
  -> gold_analytics_marts
  -> semantic_catalog
```

The current SQL ELT runner executes ordered SQL files from `sql/bronze`,
`sql/silver`, and `sql/gold`. Dagster wraps that existing implementation so the
project gains lineage visibility without duplicating transformation logic.

As dbt adoption matures, individual dbt models can replace the coarse-grained
`silver_warehouse` and `gold_analytics_marts` assets.
