"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { MarkdownSummary } from "../components/markdown-summary";
import { QueryResultTable } from "../components/query-result-table";
import { SqlPanel } from "../components/sql-panel";
import { QueryResponse } from "../types/query";
import { askQuestion } from "../lib/api";

const starterQuestions = [
  "Which product categories generate the highest revenue?",
  "Show monthly revenue growth",
  "Which states have the best average review score?",
];

console.log(
  process.env.NEXT_PUBLIC_API_URL
);

function elapsedMs(startedAt: number) {
  return Math.round(performance.now() - startedAt);
}

function formatMs(value: number | undefined) {
  if (value === undefined) {
    return "-";
  }
  return `${value.toLocaleString()} ms`;
}

function TimingPanel({
  serverTimings,
  clientTimings,
}: {
  serverTimings: Record<string, number>;
  clientTimings: Record<string, number> | null;
}) {
  const clientEntries = clientTimings ? Object.entries(clientTimings) : [];
  const serverEntries = Object.entries(serverTimings);

  return (
    <section className="timingPanel">
      <div className="timingHeader">
        <div>
          <p className="eyebrow">Debug Timing</p>
          <h2>Request phases</h2>
        </div>
      </div>

      <div className="timingGrid">
        <div>
          <h3>Browser + Next</h3>
          <dl>
            {clientEntries.map(([key, value]) => (
              <div key={key}>
                <dt>{key}</dt>
                <dd>{formatMs(value)}</dd>
              </div>
            ))}
          </dl>
        </div>

        <div>
          <h3>Backend</h3>
          <dl>
            {serverEntries.map(([key, value]) => (
              <div key={key}>
                <dt>{key}</dt>
                <dd>{formatMs(value)}</dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </section>
  );
}

export default function AnalyticsWorkspace() {
  const [question, setQuestion] = useState(starterQuestions[0]);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [clientTimings, setClientTimings] = useState<Record<string, number> | null>(null);
  const submitStartedAtRef = useRef<number | null>(null);

  useEffect(() => {
    if (!response || submitStartedAtRef.current === null) {
      return;
    }

    setClientTimings((current) => ({
      ...(current ?? {}),
      browser_total_to_render_ms: elapsedMs(submitStartedAtRef.current ?? performance.now()),
    }));
    submitStartedAtRef.current = null;
  }, [response]);

  async function submitQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const submitStartedAt = performance.now();
    submitStartedAtRef.current = submitStartedAt;
    setError(null);
    setClientTimings(null);
    setIsLoading(true);

    try {
      const fetchStartedAt = performance.now();
      const result = await askQuestion(question);
      const responseReceivedAt = performance.now();

      const parseStartedAt = performance.now();
      const payload = result;
      const payloadParsedAt = performance.now();

      setClientTimings({
        browser_submit_to_fetch_ms: Math.round(fetchStartedAt - submitStartedAt),
        browser_waiting_for_response_ms: Math.round(responseReceivedAt - fetchStartedAt),
        browser_json_parse_ms: Math.round(payloadParsedAt - parseStartedAt),
        browser_total_to_payload_ms: Math.round(payloadParsedAt - submitStartedAt),
      });

      setResponse(payload);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unexpected error");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="workspace">
      <section className="questionPane">
        <div>
          <p className="eyebrow">AI Analytics Workspace</p>
          <h1>Ask the Olist warehouse</h1>
        </div>

        <form onSubmit={submitQuestion} className="questionForm">
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            rows={5}
            aria-label="Analytics question"
          />
          <button disabled={isLoading || question.trim().length < 3}>
            {isLoading ? "Running..." : "Run query"}
          </button>
        </form>

        <div className="starterList">
          {starterQuestions.map((item) => (
            <button key={item} type="button" onClick={() => setQuestion(item)}>
              {item}
            </button>
          ))}
        </div>
      </section>

      <section className="resultPane">
        {error ? <div className="errorBox">{error}</div> : null}

        {response ? (
          <>
            <div className="summaryBand">
              <div>
                <p className="eyebrow">Summary</p>
                <MarkdownSummary content={response.summary} />
              </div>
            </div>

            <SqlPanel sql={response.sql} />
            {response.debug ? (
              <TimingPanel
                serverTimings={response.timings}
                clientTimings={clientTimings}
              />
            ) : null}
            <QueryResultTable rows={response.rows} />
          </>
        ) : (
          <div className="emptyState">
            Ask a business question to see generated SQL, result rows, chart intent,
            and execution metadata.
          </div>
        )}
      </section>
    </main>
  );
}
