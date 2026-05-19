import { NextRequest, NextResponse } from "next/server";
import { getApiUrl } from "../../../lib/api-config";

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
};

export async function POST(request: NextRequest) {
  const body = await request.json();
  const demoMode = process.env.ANALYTICS_DEMO_MODE === "true";
  const apiUrl = process.env.ANALYTICS_API_URL ?? getApiUrl();

  if (demoMode) {
    return NextResponse.json({ ...demoResponse, question: body.question });
  }

  try {
    const upstream = await fetch(`${apiUrl.replace(/\/$/, "")}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });

    const payload = await upstream.json();

    return NextResponse.json(payload, { status: upstream.status });
  } catch (error) {
    return NextResponse.json(
      {
        detail:
          error instanceof Error
            ? `Could not reach analytics backend at ${apiUrl}: ${error.message}`
            : `Could not reach analytics backend at ${apiUrl}`,
      },
      { status: 502 }
    );
  }
}
