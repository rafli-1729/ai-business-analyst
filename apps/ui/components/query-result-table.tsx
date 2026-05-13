type Props = {
  rows: Array<Record<string, unknown>>;
};

function formatLabel(value: string) {
  return value
    .replace(/_/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
    .replace(/\bId\b/g, "ID")
    .replace(/\bUsd\b/g, "USD");
}

function formatCell(column: string, value: unknown) {
  if (value === null || value === undefined) {
    return "";
  }

  if (typeof value === "number") {
    return new Intl.NumberFormat("en-US", {
      maximumFractionDigits: 2,
    }).format(value);
  }

  if (typeof value === "string") {
    const shouldHumanize =
      !column.toLowerCase().endsWith("_id") &&
      /^[a-z0-9]+(_[a-z0-9]+)+$/.test(value);

    return shouldHumanize ? formatLabel(value) : value;
  }

  return String(value);
}

export function QueryResultTable({ rows }: Props) {
  if (rows.length === 0) {
    return <div className="emptyState">No rows returned.</div>;
  }

  const columns = Object.keys(rows[0]);

  return (
    <div className="tableShell">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{formatLabel(column)}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index}>
              {columns.map((column) => (
                <td key={column}>{formatCell(column, row[column])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
