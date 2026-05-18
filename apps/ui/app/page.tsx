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
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ChartRenderer } from "../components/chart-renderer";
import { MarkdownSummary } from "../components/markdown-summary";

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

  const handleSubmit = async () => {
    setLoading(true);
    setArtifacts([]);
    setActiveAgents([]);
    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      const data = await response.json();
      setArtifacts(data.summary || []);
      setActiveAgents(data.active_agents || []);
    } catch (error) {
      setArtifacts([
        {
          name: "Error",
          type: "executive_summary",
          content: "Failed to connect to analytics engine.",
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
        ].includes(a.type),
    );
  }

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
        {/* Left Panel: Dashboard Artifacts */}
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
              p: 2,
              flexShrink: 0,
              background: "rgba(255, 255, 255, 0.03)",
              backdropFilter: "blur(10px)",
              borderRadius: 3,
              border: "1px solid rgba(255, 255, 255, 0.1)",
            }}
          >
            <Typography variant="h4" sx={{ fontWeight: 700, color: "#fff" }}>
              Dashboard
            </Typography>
          </Paper>

          <Box
            sx={{
              flex: 1,
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
            }}
          >
            {loading ? (
              <Paper
                sx={{
                  flex: 1,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  background: "rgba(255, 255, 255, 0.03)",
                  borderRadius: 3,
                  border: "1px solid rgba(255, 255, 255, 0.1)",
                }}
              >
                <Box
                  sx={{
                    width: "80px",
                    height: "80px",
                    border: "4px solid rgba(185, 103, 255, 0.1)",
                    borderTopColor: "#b967ff",
                    borderRadius: "50%",
                    animation: "spin 1s linear infinite",
                    "@keyframes spin": {
                      "0%": { transform: "rotate(0deg)" },
                      "100%": { transform: "rotate(360deg)" },
                    },
                  }}
                />
              </Paper>
            ) : dashboardArtifacts.length > 0 ? (
              (() => {
                const charts = dashboardArtifacts.filter(a => a.type === 'chart');
                const nonCharts = dashboardArtifacts.filter(a => a.type !== 'chart');

                if (charts.length === 2) {
                  return (
                    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 2, overflow: 'hidden' }}>
                      {/* Card 1: Interpretation Left (Wider), Chart Right */}
                      <Paper sx={{
                        display: 'grid',
                        gridTemplateColumns: '1.5fr 1fr',
                        flex: 1,
                        background: 'rgba(255, 255, 255, 0.03)',
                        borderRadius: 3,
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        overflow: 'hidden'
                      }}>
                        <Box sx={{ p: 2, overflow: 'hidden', borderRight: '1px solid rgba(255,255,255,0.05)', display: 'flex', flexDirection: 'column' }}>
                          <Box sx={{ flex: 1, overflow: 'hidden' }}>
                            {firstHalf.map((artifact, i) => (
                              <Box key={`nh1-${i}`} sx={{ mb: 1 }}>
                                {artifact.type === 'dashboard_explanation' && <ReactMarkdown remarkPlugins={[remarkGfm]}>{artifact.content}</ReactMarkdown>}
                                {artifact.type === 'table' && <Box sx={{ overflow: 'hidden' }}><MarkdownSummary content={artifact.content} /></Box>}
                              </Box>
                            ))}
                          </Box>
                        </Box>
                        <Box
                          sx={{
                            p: 1,
                            display: "flex",
                            flexDirection: "column",
                            overflow: "hidden",
                          }}
                        >
                          <ChartRenderer chartData={charts[0].content} />
                        </Box>
                      </Paper>

                      {/* Card 2: Chart Left, Interpretation Right (Wider) */}
                      <Paper sx={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 1.5fr',
                        flex: 1,
                        background: 'rgba(255, 255, 255, 0.03)',
                        borderRadius: 3,
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        overflow: 'hidden'
                      }}>
                        <Box sx={{ p: 1, display: 'flex', flexDirection: 'column', borderRight: '1px solid rgba(255,255,255,0.05)', overflow: 'hidden' }}>
                          <ChartRenderer chartData={charts[1].content} />
                        </Box>
                        <Box sx={{ p: 2, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                          <Box sx={{ flex: 1, overflow: 'hidden' }}>
                            {secondHalf.map((artifact, i) => (
                              <Box key={`nh2-${i}`} sx={{ mb: 1 }}>
                                {artifact.type === 'dashboard_explanation' && <ReactMarkdown remarkPlugins={[remarkGfm]}>{artifact.content}</ReactMarkdown>}
                                {artifact.type === 'table' && <Box sx={{ overflow: 'hidden' }}><MarkdownSummary content={artifact.content} /></Box>}
                              </Box>
                            ))}
                          </Box>
                        </Box>
                      </Paper>
                    </Box>
                  );
                }

                return (
                  <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 2, overflow: 'hidden' }}>
                    {dashboardArtifacts.map((artifact, i) => (
                      <Paper key={i} sx={{
                          p: 2, display: 'flex', flexDirection: 'column',
                          flex: 1,
                          background: 'rgba(255, 255, 255, 0.03)',
                          borderRadius: 3,
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          overflow: 'hidden'
                      }}>
                        {artifact.type === 'dashboard_explanation' && (
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>{artifact.content}</ReactMarkdown>
                        )}
                        {artifact.type === 'chart' && (
                          <ChartRenderer chartData={artifact.content} />
                        )}
                        {artifact.type === 'table' && (
                          <Box sx={{ overflow: 'hidden' }}>
                            <MarkdownSummary content={artifact.content} />
                          </Box>
                        )}
                      </Paper>
                    ))}
                  </Box>
                );
              })()
            ) : (
              <Paper
                sx={{
                  display: "flex",
                  flex: 1,
                  alignItems: "center",
                  justifyContent: "center",
                  background: "rgba(255, 255, 255, 0.03)",
                  borderRadius: 3,
                  border: "1px solid rgba(255, 255, 255, 0.1)",
                }}
              >
                <Typography
                  sx={{ fontStyle: "italic", opacity: 0.5, fontSize: "1.2rem" }}
                >
                  Visualizations will appear here...
                </Typography>
              </Paper>
            )}
          </Box>
        </Box>

        {/* Right Panel: Analytics & Chat */}
        <Paper
          sx={{
            flex: 1,
            p: 2,
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
          <Typography
            variant="h4"
            sx={{ fontWeight: 700, color: "#fff", mb: 1 }}
          >
            Analytics
          </Typography>

          <Box
            sx={{
              flex: 1,
              overflow: "hidden",
              p: 3,
              border: "1px solid rgba(255, 255, 255, 0.1)",
              borderRadius: 2,
              color: "#d0d0d0",
              bgcolor: "rgba(0,0,0,0.3)",
            }}
          >
            {analyticsArtifacts.length > 0 ? (
              analyticsArtifacts.map((artifact, i) => (
                <Box key={i} sx={{ mb: 2 }}>
                  <Typography
                    variant="subtitle2"
                    sx={{ color: "#b967ff", mb: 1, fontWeight: "bold" }}
                  >
                    {artifact.name}
                  </Typography>
                  <Typography sx={{ lineHeight: 1.8, fontSize: "1.05rem" }}>
                    {artifact.content}
                  </Typography>
                </Box>
              ))
            ) : (
              <Box
                sx={{
                  display: "flex",
                  height: "100%",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Typography sx={{ fontStyle: "italic", opacity: 0.5 }}>
                  Ask a question to generate an executive summary...
                </Typography>
              </Box>
            )}
          </Box>

          {/* Active Agents Indicator */}
          {activeAgents.length > 0 && (
            <Box
              sx={{
                display: "flex",
                gap: 1,
                flexWrap: "wrap",
                p: 1.5,
                bgcolor: "rgba(255,255,255,0.05)",
                borderRadius: 2,
              }}
            >
              <Typography
                sx={{
                  fontSize: "0.85rem",
                  color: "#aaa",
                  alignSelf: "center",
                  fontWeight: "bold",
                }}
              >
                Orchestrated by:
              </Typography>
              {activeAgents.map((agent) => (
                <Chip
                  key={agent}
                  label={agent}
                  size="small"
                  sx={{ bgcolor: "#b967ff", color: "#fff", fontWeight: "bold" }}
                />
              ))}
            </Box>
          )}

          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <TextField
              fullWidth
              multiline
              rows={3}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Show me the top 5 product categories by revenue..."
              sx={{
                "& .MuiOutlinedInput-root": {
                  bgcolor: "rgba(255,255,255,0.05)",
                  fontSize: "1rem",
                  borderRadius: 2,
                  "& fieldset": { borderColor: "rgba(255,255,255,0.2)" },
                  "&:hover fieldset": { borderColor: "#b967ff" },
                  "&.Mui-focused fieldset": { borderColor: "#b967ff" },
                },
                "& .MuiInputBase-input": { minHeight: "60px", color: "#fff" },
              }}
            />
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={loading || !query.trim()}
              sx={{
                py: 1.5,
                fontWeight: 700,
                fontSize: "1rem",
                borderRadius: 2,
                bgcolor: "#b967ff",
                "&:hover": { bgcolor: "#9a4deb" },
              }}
            >
              {loading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                "Run Analysis"
              )}
            </Button>
          </Box>
        </Paper>
      </Box>
    </ThemeProvider>
  );
}
