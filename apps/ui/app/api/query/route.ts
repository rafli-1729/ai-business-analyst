import { NextRequest, NextResponse } from "next/server";

const demoResponse = {
  question: "Which product categories generate the highest revenue?",
  sql: "select product_category_name, sum(order_item_revenue) as revenue from gold.order_item_facts group by 1 order by 2 desc limit 10",
  summary: "Revenue is concentrated in the highest-volume product categories.",
  rows: [
    { product_category_name: "health_beauty", revenue: 125000 },
    { product_category_name: "watches_gifts", revenue: 118000 },
    { product_category_name: "bed_bath_table", revenue: 106000 }
  ],
  chart_type: "bar",
  row_count: 3,
  execution_ms: 42,
  schema_version: "demo",
  debug: process.env.DEBUG === "true",
  is_truncated: false,
  cache_hit: false,
  sql_cache_hit: false,
  timings: {
    sql_generation_ms: 12,
    db_execution_ms: 8,
    summary_ms: 20,
    total_ms: 42
  }
};

function elapsedMs(startedAt: number) {
  return Math.round(performance.now() - startedAt);
}

function withProxyTiming(payload: unknown, timings: Record<string, number>) {
  if (payload && typeof payload === "object" && !Array.isArray(payload)) {
    const body = payload as Record<string, unknown>;
    if (body.debug !== true) {
      return body;
    }

    const existingTimings =
      body.timings && typeof body.timings === "object" && !Array.isArray(body.timings)
        ? (body.timings as Record<string, number>)
        : {};

    return {
      ...body,
      timings: {
        ...existingTimings,
        ...timings,
      },
    };
  }

  return payload;
}

export async function POST(request: NextRequest) {
  const routeStartedAt = performance.now();
  const bodyStartedAt = performance.now();
  const body = await request.json();
  const timings: Record<string, number> = {
    next_api_read_body_ms: elapsedMs(bodyStartedAt),
  };
  const demoMode = process.env.ANALYTICS_DEMO_MODE === "true";
  const apiUrl = process.env.ANALYTICS_API_URL ?? "http://localhost:8000";

  if (demoMode) {
    timings.next_api_total_ms = elapsedMs(routeStartedAt);
    return NextResponse.json(
      withProxyTiming({ ...demoResponse, question: body.question }, timings)
    );
  }

  try {
    const upstreamStartedAt = performance.now();
    const upstream = await fetch(`${apiUrl.replace(/\/$/, "")}/api/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });
    timings.next_api_upstream_fetch_ms = elapsedMs(upstreamStartedAt);

    const jsonStartedAt = performance.now();
    const payload = await upstream.json();
    timings.next_api_upstream_json_ms = elapsedMs(jsonStartedAt);
    timings.next_api_total_ms = elapsedMs(routeStartedAt);

    return NextResponse.json(withProxyTiming(payload, timings), { status: upstream.status });
  } catch (error) {
    timings.next_api_total_ms = elapsedMs(routeStartedAt);
    return NextResponse.json(
      withProxyTiming({
        detail:
          error instanceof Error
            ? `Could not reach analytics backend at ${apiUrl}: ${error.message}`
            : `Could not reach analytics backend at ${apiUrl}`,
      }, timings),
      { status: 502 }
    );
  }
}
