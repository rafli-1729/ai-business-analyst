"use client";
import { useState } from "react";
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  CircularProgress,
  CssBaseline,
  ThemeProvider,
  createTheme,
  Chip,
  Divider,
} from "@mui/material";
import ErrorOutlined from "@mui/icons-material/ErrorOutlined";
import BarChartOutlined from "@mui/icons-material/BarChartOutlined";
import AssignmentOutlined from "@mui/icons-material/AssignmentOutlined";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ChartRenderer } from "../components/chart-renderer";
import { MarkdownSummary } from "../components/markdown-summary";
import { getApiUrl } from "../lib/api-config";

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#b967ff" },
    background: {
      default: "#0a0a0c",
      paper: "#121214",
    },
  },
  typography: {
    fontFamily: '"Source Serif 4", "Georgia", "serif"',
  },
});

export default function AnalyticsWorkspace() {
  const [query, setQuery] = useState("");
  const [artifacts, setArtifacts] = useState<any[]>([]);
  const [activeAgents, setActiveAgents] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    setHasSearched(true);
    try {
      const apiUrl = getApiUrl();
      const response = await fetch(`${apiUrl.replace(/\/$/, '')}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      const data = await response.json();
      setArtifacts(data.summary || []);
      setActiveAgents(data.active_agents || []);
    } catch (error: any) {
      console.error("Fetch Error:", error);
      const apiUrl = getApiUrl();
      setArtifacts([
        {
          name: "Connection Error",
          type: "executive_summary",
          content: `Failed to connect to analytics engine at **${apiUrl}**. \n\n**Possible causes:**\n1. Backend server is not running.\n2. API URL is misconfigured.\n3. Network/CORS issues.\n\n**Details:** ${error.message || error}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const dashboardArtifacts = artifacts.filter((a) =>
    ["chart", "table", "dashboard_explanation"].includes(a.type),
  );

  let analyticsArtifacts = artifacts.filter(
    (a) => a.type === "unified_executive_summary",
  );
  if (analyticsArtifacts.length === 0) {
    analyticsArtifacts = artifacts.filter(
      (a) =>
        ["executive_summary", "insight"].includes(a.type) ||
        ![
          "chart",
          "table",
          "dashboard_explanation",
          "unified_executive_summary",
          "raw_data"
        ].includes(a.type),
    );
  }

  const rawData = artifacts.find(a => a.type === "raw_data");
  const charts = dashboardArtifacts.filter(a => a.type === 'chart');

  const downloadableItems = charts.length > 0 
    ? charts.map((c, i) => ({ name: c.content.title || `Chart_Data_${i+1}`, data: c.content.data }))
    : rawData && rawData.content ? [{ name: "olist_data_export", data: rawData.content }] : [];

  const handleDownloadCSV = (dataToDownload: any[], fileName: string) => {
    if (!dataToDownload || dataToDownload.length === 0) return;
    const headers = Object.keys(dataToDownload[0]);
    const csvRows = dataToDownload.map((row: any) => 
      headers.map(fieldName => JSON.stringify(row[fieldName] || '')).join(',')
    );
    const csvString = [headers.join(','), ...csvRows].join('\r\n');
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    const cleanFileName = fileName.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    link.setAttribute('download', `${cleanFileName}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          display: "flex",
          height: "100vh",
          p: 2,
          gap: 2,
          background: "linear-gradient(135deg, #0a0a0c 0%, #1a1a2e 100%)",
          overflow: "hidden",
        }}
      >
        {/* Left Panel: Analysis Dashboard */}
        <Box
          sx={{
            flex: 3,
            display: "flex",
            flexDirection: "column",
            gap: 2,
            height: "100%",
            overflow: "hidden",
          }}
        >
          <Paper
            sx={{
              p: 1.5,
              flexShrink: 0,
              background: "rgba(255, 255, 255, 0.03)",
              backdropFilter: "blur(10px)",
              borderRadius: 3,
              border: "1px solid rgba(255, 255, 255, 0.1)",
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            <Typography variant="h5" sx={{ fontWeight: 700, color: "#fff" }}>
              Analytics Intelligence
            </Typography>
          </Paper>

          <Box
            sx={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              gap: 2,
              overflow: "hidden",
            }}
          >
            {dashboardArtifacts.length > 0 ? (
              (() => {
                const explanations = dashboardArtifacts.filter(a => a.type === 'dashboard_explanation');
                const tables = dashboardArtifacts.filter(a => a.type === 'table');

                const renderExplanation = (exp: any) => {
                  if (!exp) return null;
                  let content = exp.content;
                  if (Array.isArray(content)) content = content.join('\n\n');
                  else if (typeof content !== 'string') content = JSON.stringify(content);
                  
                  return (
                    <Box sx={{ p: 2, bgcolor: "rgba(0,0,0,0.1)", borderRadius: 2 }}>
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
                    </Box>
                  );
                };

                return (
                  <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 2 }}>
                    
                    {charts.length === 1 && (
                      <Paper sx={{ p: 3, flex: 1, background: 'rgba(255, 255, 255, 0.03)', borderRadius: 3, border: "1px solid rgba(255, 255, 255, 0.1)", display: 'flex', flexDirection: 'column', gap: 2 }}>
                        <Box sx={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column", p: 0 }}>
                          <ChartRenderer chartData={charts[0].content} />
                        </Box>
                        <Box sx={{ maxHeight: '30%', overflowY: 'auto' }}>
                          {explanations.map((exp, i) => <Box key={`exp-${i}`}>{renderExplanation(exp)}</Box>)}
                        </Box>
                      </Paper>
                    )}

                    {charts.length >= 2 && (
                      <>
                        <Paper sx={{ p: 2.5, flex: 1, background: 'rgba(255, 255, 255, 0.03)', borderRadius: 3, border: "1px solid rgba(255, 255, 255, 0.1)", display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 4 }}>
                          <Box sx={{ minHeight: 0, display: "flex", flexDirection: "column", p: 0 }}>
                            <ChartRenderer chartData={charts[0].content} />
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'flex-start', overflowY: 'auto' }}>
                            {explanations.length > 0 && renderExplanation(explanations[0])}
                          </Box>
                        </Paper>

                        <Paper sx={{ p: 2.5, flex: 1, background: 'rgba(255, 255, 255, 0.03)', borderRadius: 3, border: "1px solid rgba(255, 255, 255, 0.1)", display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 4 }}>
                          <Box sx={{ display: 'flex', alignItems: 'flex-start', overflowY: 'auto' }}>
                            {explanations.length > 1 ? renderExplanation(explanations[1]) : (explanations.length > 0 ? renderExplanation(explanations[0]) : null)}
                          </Box>
                          <Box sx={{ minHeight: 0, display: "flex", flexDirection: "column", p: 0 }}>
                            <ChartRenderer chartData={charts[1].content} />
                          </Box>
                        </Paper>
                      </>
                    )}

                    {charts.length === 0 && (
                      <Paper sx={{ p: 3, flex: 1, background: 'rgba(255, 255, 255, 0.03)', borderRadius: 3, border: "1px solid rgba(255, 255, 255, 0.1)", overflowY: 'auto' }}>
                        <Box>{explanations.map((exp, i) => <Box key={`exp-${i}`}>{renderExplanation(exp)}</Box>)}</Box>
                        {tables.map((tbl, i) => <Box key={`tbl-${i}`} sx={{ mt: 2 }}><MarkdownSummary content={tbl.content} /></Box>)}
                      </Paper>
                    )}
                  </Box>
                );              
              })()
            ) : loading ? (
              <Paper sx={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(255, 255, 255, 0.03)", borderRadius: 3, border: "1px solid rgba(255, 255, 255, 0.1)" }}>
                <Box sx={{ textAlign: 'center' }}>
                  <CircularProgress size={60} thickness={2} sx={{ mb: 2, color: "#b967ff" }} />
                  <Typography sx={{ opacity: 0.6 }}>Mining insights from the warehouse...</Typography>
                </Box>
              </Paper>
            ) : (
              <Paper sx={{ display: "flex", flex: 1, flexDirection: 'column', alignItems: "center", justifyContent: "center", background: "rgba(255, 255, 255, 0.03)", borderRadius: 3, border: "1px solid rgba(255, 255, 255, 0.1)", p: 4 }}>
                {hasSearched ? (
                  <>
                    <ErrorOutlined sx={{ fontSize: 60, mb: 2, opacity: 0.2 }} />
                    <Typography variant="h6" sx={{ opacity: 0.5, mb: 1 }}>Data Unavailable</Typography>
                    <Typography sx={{ opacity: 0.4, textAlign: 'center', maxWidth: 400 }}>
                      We couldn't retrieve enough meaningful data to build a visualization for this specific request. Try adjusting your filters or checking for data in other periods.
                    </Typography>
                  </>
                ) : (
                  <>
                    <BarChartOutlined sx={{ fontSize: 60, mb: 2, opacity: 0.1 }} />
                    <Typography sx={{ fontStyle: "italic", opacity: 0.3, fontSize: "1.1rem" }}>Visual insights will appear here after analysis...</Typography>
                  </>
                )}
              </Paper>
            )}
          </Box>
        </Box>

        {/* Right Panel: Executive Summary */}
        <Paper
          sx={{
            flex: 1.2,
            p: 2.5,
            display: "flex",
            flexDirection: "column",
            gap: 2,
            background: "rgba(255, 255, 255, 0.03)",
            backdropFilter: "blur(10px)",
            borderRadius: 3,
            border: "1px solid rgba(255, 255, 255, 0.1)",
            overflow: "hidden",
          }}
        >
          <Typography variant="h5" sx={{ fontWeight: 700, color: "#fff", mb: 0.5 }}>
            Executive Summary
          </Typography>

          <Box
            sx={{
              flex: 1,
              color: "#e0e0e0",
              overflowY: "auto",
              '&::-webkit-scrollbar': { width: '4px' }, '&::-webkit-scrollbar-thumb': { bgcolor: 'rgba(255,255,255,0.05)' }
            }}
          >
            {analyticsArtifacts.length > 0 ? (
              analyticsArtifacts.map((artifact, i) => (
                <Box key={i} sx={{ mb: 3 }}>
                  {!artifact.name.toLowerCase().includes("executive summary") && (
                    <Typography variant="subtitle2" sx={{ color: "#b967ff", mb: 1, fontWeight: "bold", textTransform: "uppercase", letterSpacing: 1 }}>
                      {artifact.name}
                    </Typography>
                  )}
                  <Box sx={{ 
                    lineHeight: 1.7, 
                    fontSize: "1rem", 
                    opacity: 0.9,
                    '& p': { mb: 2 },
                    '& strong': { color: '#b967ff' }
                  }}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{artifact.content}</ReactMarkdown>
                  </Box>
                </Box>
              ))
            ) : (
              <Box sx={{ display: "flex", height: "100%", flexDirection: 'column', alignItems: "center", justifyContent: "center", opacity: 0.2 }}>
                <AssignmentOutlined sx={{ fontSize: 48, mb: 1 }} />
                <Typography sx={{ fontStyle: "italic", textAlign: 'center', px: 2 }}>
                  {loading ? "Synthesizing strategic narrative..." : (hasSearched ? "No qualitative insights could be generated for this specific query." : "Strategic narrative will appear here after analysis.")}
                </Typography>
              </Box>
            )}
          </Box>

          {activeAgents.length > 0 && (
            <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap", p: 1, bgcolor: "rgba(255,255,255,0.03)", borderRadius: 2 }}>
              <Typography sx={{ fontSize: "0.75rem", color: "#888", alignSelf: "center", fontWeight: "bold" }}>Agents:</Typography>
              {activeAgents.map((agent) => (
                <Chip key={agent} label={agent} size="small" sx={{ height: 20, fontSize: '0.7rem', bgcolor: "rgba(185, 103, 255, 0.2)", color: "#b967ff", fontWeight: "bold", border: "1px solid rgba(185, 103, 255, 0.3)" }} />
              ))}
            </Box>
          )}

          <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
            {downloadableItems.length > 0 && (
              <Box sx={{ display: "flex", gap: 1, mb: 0.5, width: "100%" }}>
                {downloadableItems.slice(0, 2).map((item, idx) => (
                  <Button 
                    key={idx}
                    fullWidth
                    variant="outlined" 
                    size="small" 
                    onClick={() => handleDownloadCSV(item.data, item.name)}
                    sx={{ 
                      borderRadius: "10px", 
                      py: 0.75,
                      fontSize: '0.75rem',
                      color: "#b967ff", 
                      borderColor: "rgba(185, 103, 255, 0.3)", 
                      bgcolor: "rgba(185, 103, 255, 0.03)",
                      textTransform: "none",
                      "&:hover": { borderColor: "#b967ff", bgcolor: "rgba(185, 103, 255, 0.1)" } 
                    }}
                  >
                    ↓ {item.name.length > 15 ? item.name.substring(0, 15) + '...' : item.name}
                  </Button>
                ))}
              </Box>
            )}
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                multiline
                maxRows={4}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about top 7 products, revenue trends..."
                sx={{
                  "& .MuiOutlinedInput-root": {
                    bgcolor: "rgba(255,255,255,0.03)",
                    fontSize: "0.95rem",
                    borderRadius: 2.5,
                    "& fieldset": { borderColor: "rgba(255,255,255,0.1)" },
                    "&:hover fieldset": { borderColor: "rgba(185, 103, 255, 0.5)" },
                    "&.Mui-focused fieldset": { borderColor: "#b967ff" },
                  },
                  "& .MuiInputBase-input": { color: "#fff" },
                }}
              />
              <Button
                variant="contained"
                onClick={handleSubmit}
                disabled={loading || !query.trim()}
                sx={{
                  minWidth: "60px",
                  width: "60px",
                  height: "auto",
                  borderRadius: 2.5,
                  bgcolor: "#b967ff",
                  "&:hover": { bgcolor: "#9a4deb" },
                }}
              >
                {loading ? <CircularProgress size={20} color="inherit" /> : <Typography variant="h6" sx={{ fontWeight: 900, lineHeight: 1 }}>↑</Typography>}
              </Button>
            </Box>
          </Box>
        </Paper>
      </Box>
    </ThemeProvider>
  );
}
