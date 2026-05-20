"use client";

import { Box, Button, alpha } from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";

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
    return (
      <Box sx={{ p: 4, textAlign: 'center', opacity: 0.5 }}>
        No rows returned.
      </Box>
    );
  }

  const columns = Object.keys(rows[0]);
  const displayRows = rows.slice(0, 5); // UI only shows top 5

  const handleDownload = () => {
    // Download uses the FULL rows array
    const headers = columns.join(",");
    const csvRows = rows.map(row => 
      columns.map(col => {
        const val = row[col];
        return typeof val === 'string' ? `"${val.replace(/"/g, '""')}"` : val;
      }).join(",")
    );
    const csvContent = [headers, ...csvRows].join("\n");
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `query_results_${Date.now()}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Box sx={{ width: "100%", display: "flex", flexDirection: "column", gap: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: 1 }}>
        {rows.length > 5 && (
           <Box sx={{ fontSize: '0.65rem', color: 'text.secondary', opacity: 0.5 }}>
             Showing 5 of {rows.length} rows
           </Box>
        )}
        <Button 
          size="small" 
          startIcon={<DownloadIcon />} 
          onClick={handleDownload}
          sx={{ 
            color: 'text.secondary', 
            fontSize: '0.65rem',
            p: '2px 8px',
            '&:hover': { color: 'primary.main', bgcolor: alpha('#fff', 0.05) }
          }}
        >
          CSV
        </Button>
      </Box>
      <Box sx={{ 
        width: "100%", 
        overflowX: "auto",
        borderRadius: 0,
        border: `1px solid ${alpha('#fff', 0.05)}`,
        bgcolor: alpha('#000', 0.2)
      }}>
        <Box
          component="table"
          sx={{
            width: "100%",
            borderCollapse: "collapse",
            fontSize: "0.75rem",
            "& th": {
              p: 1.5,
              textAlign: "left",
              color: "primary.main",
              fontWeight: 700,
              borderBottom: `1px solid ${alpha('#fff', 0.05)}`,
              bgcolor: alpha('#fff', 0.01),
              whiteSpace: 'nowrap'
            },
            "& td": {
              p: 1.5,
              color: "text.secondary",
              borderBottom: `1px solid ${alpha('#fff', 0.02)}`,
              whiteSpace: 'nowrap'
            },
            "& tr:last-child td": {
              borderBottom: 'none'
            }
          }}
        >
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column}>{formatLabel(column)}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {displayRows.map((row, index) => (
              <tr key={index}>
                {columns.map((column) => (
                  <td key={column}>{formatCell(column, row[column])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </Box>
      </Box>
    </Box>
  );
}
