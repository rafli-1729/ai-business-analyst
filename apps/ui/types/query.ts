export type QueryResponse = {
  question: string;
  sql: string;
  summary: string;
  rows: Array<Record<string, unknown>>;
  chart_type: "bar" | "line" | "table";
  row_count: number;
  execution_ms: number;
  schema_version: string;
  debug: boolean;
  is_truncated: boolean;
  cache_hit: boolean;
  sql_cache_hit: boolean;
};
