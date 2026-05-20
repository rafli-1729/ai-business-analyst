"use client";
import { useState, useEffect, useMemo } from "react";
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
  alpha,
  Skeleton,
} from "@mui/material";
import BarChartOutlined from "@mui/icons-material/BarChartOutlined";
import AssignmentOutlined from "@mui/icons-material/AssignmentOutlined";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import ErrorOutlinedIcon from "@mui/icons-material/ErrorOutlined";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ChartRenderer } from "../components/chart-renderer";
import { QueryResultTable } from "../components/query-result-table";
import { getApiUrl } from "../lib/api-config";

// 2025 Premium Design Tokens
const TOKENS = {
  radius: 40, 
  padding: 40, 
  midnight: "#040508",
  accent: "#c084fc",
  glass: alpha("#111218", 0.4),
  border: "rgba(255, 255, 255, 0.06)",
};

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: TOKENS.accent },
    background: { default: TOKENS.midnight, paper: TOKENS.glass },
    text: { primary: "#ffffff", secondary: "#94a3b8" },
  },
  typography: {
    fontFamily: '"Inter", "Geist Sans", sans-serif',
    h5: { fontWeight: 900, letterSpacing: "-0.05em", fontSize: "2rem" },
    h6: { fontWeight: 700, letterSpacing: "-0.03em" },
    subtitle2: { fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", fontSize: "0.75rem" },
  },
  shape: { borderRadius: TOKENS.radius },
});

const bentoCard = {
  display: "flex",
  flexDirection: "column",
  background: `linear-gradient(165deg, ${alpha("#1e1b4b", 0.25)} 0%, ${alpha("#08090a", 0.4)} 100%)`,
  backdropFilter: "blur(30px) saturate(180%)",
  WebkitBackdropFilter: "blur(30px) saturate(180%)",
  borderRadius: `${TOKENS.radius}px`,
  border: `1px solid ${TOKENS.border}`,
  boxShadow: `
    0 10px 40px -10px rgba(0, 0, 0, 0.5),
    inset 0 1px 1px rgba(255, 255, 255, 0.05)
  `,
  transition: "all 0.3s ease-out",
  "&:hover": {
    borderColor: alpha(TOKENS.accent, 0.2),
    transform: "translateY(-2px)",
    boxShadow: `0 20px 60px -15px rgba(0, 0, 0, 0.7)`,
  },
};

const TableSkeleton = () => (
  <Box sx={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', gap: 1 }}>
    <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
      {[1, 2, 3, 4].map((i) => (
        <Skeleton key={i} variant="rectangular" height={36} sx={{ flex: 1, bgcolor: alpha('#fff', 0.05), borderRadius: 1 }} />
      ))}
    </Box>
    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((row) => (
      <Box key={row} sx={{ display: 'flex', gap: 1 }}>
        {[1, 2, 3, 4].map((col) => (
          <Skeleton key={col} variant="rectangular" height={24} sx={{ flex: 1, bgcolor: alpha('#fff', 0.02), borderRadius: 0.5 }} />
        ))}
      </Box>
    ))}
    <Box sx={{ flex: 1 }} />
  </Box>
);

export default function AnalyticsWorkspace() {
  const [query, setQuery] = useState("");
  const [artifacts, setArtifacts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [showVisuals, setShowVisuals] = useState(false);
  const [dbName, setDbName] = useState("Data Warehouse");
  const [error, setError] = useState<string | null>(null);

  // Scroll Fade States
  const [leftScroll, setLeftScroll] = useState({ top: false, bottom: false });
  const [rightScroll, setRightScroll] = useState({ top: false, bottom: false });

  const handleScroll = (e: any, side: 'left' | 'right') => {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    const update = {
      top: scrollTop > 10,
      bottom: scrollTop + clientHeight < scrollHeight - 10
    };
    if (side === 'left') setLeftScroll(update);
    else setRightScroll(update);
  };

  const fetchConnection = async () => {
    try {
      const apiUrl = getApiUrl();
      const response = await fetch(`${apiUrl.replace(/\/$/, '')}/connection`);
      const data = await response.json();
      setDbName(data.database);
    } catch (e) {
      setDbName("Data Warehouse");
    }
  };

  const charts = useMemo(() => {
    return artifacts.filter(a => a.type === 'chart');
  }, [artifacts]);
  const explanations = useMemo(() => artifacts.filter(a => a.type === 'dashboard_explanation'), [artifacts]);
  
  const narrative = useMemo(() => (artifacts.filter(a => a.type === "unified_executive_summary").length > 0 
    ? artifacts.filter(a => a.type === "unified_executive_summary")
    : artifacts.filter(a => ["executive_summary", "insight"].includes(a.type)))
    .map(n => ({
      ...n,
      content: n.content
        .replace(/\|(.+)\|/g, '')
        .replace(/```sql[\s\S]*?```/g, '')
        .replace(/```[\s\S]*?```/g, '')
        .trim()
    }))
    .filter(n => n.content.length > 0), [artifacts]);

  const tableArtifacts = useMemo(() => artifacts.filter(a => a.type === 'table'), [artifacts]);

  useEffect(() => {
    fetchConnection();
  }, []);

  // Initialize and update scroll masks
  useEffect(() => {
    const leftEl = document.getElementById('left-scroll-container');
    const rightEl = document.getElementById('right-scroll-container');
    
    const checkScroll = (el: HTMLElement | null, side: 'left' | 'right') => {
      if (!el) return;
      const { scrollTop, scrollHeight, clientHeight } = el;
      const top = scrollTop > 10;
      const bottom = scrollTop + clientHeight < scrollHeight - 10;
      
      if (side === 'left') {
        setLeftScroll(prev => (prev.top === top && prev.bottom === bottom) ? prev : { top, bottom });
      } else {
        setRightScroll(prev => (prev.top === top && prev.bottom === bottom) ? prev : { top, bottom });
      }
    };

    const timer = setTimeout(() => {
      checkScroll(leftEl, 'left');
      checkScroll(rightEl, 'right');
    }, 100);

    return () => clearTimeout(timer);
  }, [artifacts, narrative, charts, tableArtifacts, showVisuals]);

  const handleSubmit = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setHasSearched(true);
    setShowVisuals(false);
    setError(null);
    try {
      const apiUrl = getApiUrl();
      const response = await fetch(`${apiUrl.replace(/\/$/, '')}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query,
          generate_charts: true 
        }),
      });
      const data = await response.json();
      setArtifacts(data.summary || []);
      setShowVisuals(true);
    } catch (err) {
      setError("Analysis orchestration failed. Please check connection.");
      setArtifacts([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{
        display: "flex", height: "100vh", p: 4, gap: 4,
        bgcolor: TOKENS.midnight,
        backgroundImage: `
          radial-gradient(circle at 0% 0%, ${alpha(TOKENS.accent, 0.12)}, transparent 50%),
          radial-gradient(circle at 100% 100%, ${alpha("#3b82f6", 0.1)}, transparent 50%)
        `,
        overflow: "hidden"
      }}>
        
        {/* LEFT COLUMN: Narrative & Visuals */}
        <Box sx={{ flex: 1.5, display: "flex", flexDirection: "column", gap: 2 }}>
          <Paper elevation={0} sx={{ 
            ...bentoCard, 
            p: "16px 40px", 
            m: "8px 8px 0 8px",
            borderRadius: 30,
            display: 'flex', flexDirection: 'row', alignItems: 'center', gap: 3, flexShrink: 0 
          }}>
            <AutoAwesomeIcon sx={{ color: TOKENS.accent }} />
            <Typography variant="h5">Analyst Intelligence</Typography>
            <Box sx={{ ml: 'auto', display: 'flex', gap: 1.5 }}>
              <Typography variant="caption" sx={{ color: "text.secondary", alignSelf: "center", opacity: 0.5 }}>{dbName} Connector</Typography>
            </Box>
          </Paper>

          <Box 
            id="left-scroll-container"
            onScroll={(e) => handleScroll(e, 'left')}
            sx={{ 
              flex: 1, 
              overflowY: "auto", 
              p: "12px 12px 24px 12px", 
              display: "flex", 
              flexDirection: "column", 
              gap: 2,
              transition: 'mask-image 0.3s ease',
              WebkitMaskImage: `linear-gradient(to bottom, 
                ${leftScroll.top ? 'transparent' : 'black'} 0%, 
                black 60px, 
                black calc(100% - 60px), 
                ${leftScroll.bottom ? 'transparent' : 'black'} 100%)`,
              maskImage: `linear-gradient(to bottom, 
                ${leftScroll.top ? 'transparent' : 'black'} 0%, 
                black 60px, 
                black calc(100% - 40px), 
                ${leftScroll.bottom ? 'transparent' : 'black'} 100%)`,
            }}
          >
            {!hasSearched ? (
               <Paper sx={{ 
                ...bentoCard, 
                flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', p: 6,
                borderStyle: 'dashed', borderColor: alpha(TOKENS.accent, 0.15),
                textAlign: 'center'
              }}>
                <Box sx={{ 
                  mb: 4, 
                  p: 3, 
                  borderRadius: '50%', 
                  bgcolor: alpha(TOKENS.accent, 0.05),
                  border: `1px solid ${alpha(TOKENS.accent, 0.1)}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <AutoAwesomeIcon sx={{ fontSize: 60, color: TOKENS.accent }} />
                </Box>
                
                <Typography variant="h5" sx={{ mb: 2, background: `linear-gradient(to right, #fff, ${TOKENS.accent})`, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                  Olist Warehouse Dataset
                </Typography>
                
                <Typography variant="body1" sx={{ color: 'text.secondary', maxWidth: 600, mb: 4, lineHeight: 1.6 }}>
                  Welcome to the autonomous analytical workspace. You are connected to the Olist Brazilian E-Commerce database. 
                  Ask questions in natural language to discover insights about orders, products, customers, and delivery performance.
                </Typography>

                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'center' }}>
                  {["What is the monthly revenue trend?", "Show top 5 categories by sales", "Analyze delivery delay patterns"].map((q) => (
                    <Chip 
                      key={q} 
                      label={q} 
                      onClick={() => setQuery(q)}
                      sx={{ 
                        bgcolor: alpha(TOKENS.accent, 0.05), 
                        color: TOKENS.accent,
                        border: `1px solid ${alpha(TOKENS.accent, 0.1)}`,
                        '&:hover': { bgcolor: alpha(TOKENS.accent, 0.1), borderColor: TOKENS.accent }
                      }} 
                    />
                  ))}
                </Box>

                <Box sx={{ mt: 8, opacity: 0.2 }}>
                  <Typography variant="caption" sx={{ letterSpacing: 2 }}>POWERED BY AUTONOMOUS ANALYST AGENT</Typography>
                </Box>
              </Paper>
            ) : loading ? (
              <Paper sx={{ ...bentoCard, flex: 1, p: 4, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Box sx={{ textAlign: 'center' }}>
                  <CircularProgress size={60} thickness={2} sx={{ color: TOKENS.accent }} />
                  <Typography sx={{ mt: 3, opacity: 0.4, letterSpacing: 6 }}>ORCHESTRATING...</Typography>
                </Box>
              </Paper>
            ) : error ? (
              <Paper sx={{ ...bentoCard, flex: 1, p: 4, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Box sx={{ textAlign: 'center' }}>
                  <ErrorOutlinedIcon sx={{ fontSize: 60, color: 'error.main', mb: 2, opacity: 0.5 }} />
                  <Typography color="error" variant="body1">{error}</Typography>
                </Box>
              </Paper>
            ) : (
              <>
                {narrative.length > 0 && (
                  <Paper sx={{ ...bentoCard, p: 4, bgcolor: alpha(TOKENS.accent, 0.02) }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1.5 }}>
                      <AssignmentOutlined sx={{ color: TOKENS.accent }} />
                      <Typography variant="h6">Olist Warehouse Dataset</Typography>
                    </Box>
                    <Divider sx={{ opacity: 0.05, mb: 2 }} />
                    <Box sx={{ color: "text.secondary", fontSize: "1.1rem", lineHeight: 1.8 }}>
                      {narrative.map((n, i) => (
                        <Box key={i} sx={{ mb: 3 }}>
                          <ReactMarkdown 
                            remarkPlugins={[remarkGfm]} 
                          >
                            {n.content}
                          </ReactMarkdown>
                        </Box>
                      ))}
                    </Box>
                  </Paper>
                )}

                {explanations.length > 0 && (
                  <Paper sx={{ ...bentoCard, p: 4 }}>
                    <Typography variant="subtitle2" sx={{ color: TOKENS.accent, mb: 3 }}>Analysis Deep-Dive</Typography>
                    <Box sx={{ color: "text.secondary", fontSize: "1rem", lineHeight: 1.7 }}>
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{explanations[0].content}</ReactMarkdown>
                    </Box>
                  </Paper>
                )}

                {charts.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Button 
                      startIcon={showVisuals ? <VisibilityOffIcon /> : <VisibilityIcon />}
                      onClick={() => setShowVisuals(!showVisuals)}
                      sx={{ 
                        color: TOKENS.accent, 
                        borderColor: alpha(TOKENS.accent, 0.2),
                        borderRadius: 2,
                        mb: showVisuals ? 3 : 0,
                        "&:hover": { bgcolor: alpha(TOKENS.accent, 0.05), borderColor: TOKENS.accent }
                      }}
                      variant="outlined"
                    >
                      {showVisuals ? "Hide Visual Insights" : `Show Visual Insights (${charts.length})`}
                    </Button>

                    {showVisuals && (
                      <Box sx={{ 
                        display: 'grid', 
                        gridTemplateColumns: charts.length > 1 ? '1fr 1fr' : '1fr', 
                        gap: 4,
                        minHeight: "450px",
                        flexShrink: 0
                      }}>
                        {charts.map((chart, i) => (
                          <Paper key={i} sx={{ ...bentoCard, p: 4, height: "100%", overflow: 'hidden' }}>
                            <Typography variant="subtitle2" sx={{ color: TOKENS.accent, mb: 2, opacity: 0.8 }}>
                              {chart.content.title || chart.name || `Visual Artifact #${i+1}`}
                            </Typography>
                            <Box sx={{ flex: 1, minHeight: 0, width: "100%", display: 'flex', flexDirection: 'column' }}>
                              <ChartRenderer chartData={chart.content} />
                            </Box>
                          </Paper>
                        ))}
                      </Box>
                    )}
                  </Box>
                )}
              </>
            )}
          </Box>
        </Box>

        {/* RIGHT COLUMN: Data Matrix & Input */}
        <Box sx={{ flex: 1.5, display: "flex", flexDirection: "column", gap: 4 }}>
          <Paper elevation={0} sx={{ 
            ...bentoCard, 
            p: 4,
            m: 1,
            flex: 1, display: "flex", flexDirection: "column", gap: 3, overflow: "hidden" 
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <BarChartOutlined sx={{ color: TOKENS.accent }} />
              <Typography variant="h6">Data Matrix</Typography>
            </Box>
            <Divider sx={{ opacity: 0.05 }} />

            <Box 
              id="right-scroll-container"
              onScroll={(e) => handleScroll(e, 'right')}
              sx={{ 
                flex: 1, 
                overflowY: 'auto', 
                p: 1, 
                display: 'flex', 
                flexDirection: 'column', 
                gap: 4,
                transition: 'mask-image 0.3s ease',
                WebkitMaskImage: `linear-gradient(to bottom, 
                  ${rightScroll.top ? 'transparent' : 'black'} 0%, 
                  black 40px, 
                  black calc(100% - 40px), 
                  ${rightScroll.bottom ? 'transparent' : 'black'} 100%)`,
                maskImage: `linear-gradient(to bottom, 
                  ${rightScroll.top ? 'transparent' : 'black'} 0%, 
                  black 40px, 
                  black calc(100% - 40px), 
                  ${rightScroll.bottom ? 'transparent' : 'black'} 100%)`,
              }}>
              {loading ? (
                <TableSkeleton />
              ) : tableArtifacts.length > 0 ? (
                tableArtifacts.map((art, idx) => (
                  <Box key={idx}>
                    {tableArtifacts.length > 1 && (
                       <Typography variant="subtitle2" sx={{ color: alpha(TOKENS.accent, 0.6), mb: 1, fontSize: '0.65rem' }}>
                         {art.name}
                       </Typography>
                    )}
                    <QueryResultTable rows={art.content} />
                  </Box>
                ))
              ) : !hasSearched ? (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  <Typography variant="subtitle2" sx={{ color: TOKENS.accent, opacity: 0.8 }}>Warehouse Architecture</Typography>
                  <Box
                    component="table"
                    sx={{
                      width: "100%",
                      borderCollapse: "collapse",
                      fontSize: "0.75rem",
                      border: `1px solid ${alpha('#fff', 0.05)}`,
                      bgcolor: alpha('#000', 0.2),
                      "& th": {
                        p: 1.5,
                        textAlign: "left",
                        color: "primary.main",
                        fontWeight: 700,
                        borderBottom: `1px solid ${alpha('#fff', 0.05)}`,
                        bgcolor: alpha('#fff', 0.01),
                      },
                      "& td": {
                        p: 1.5,
                        color: "text.secondary",
                        borderBottom: `1px solid ${alpha('#fff', 0.02)}`,
                        lineHeight: 1.5
                      }
                    }}
                  >
                    <thead>
                      <tr>
                        <th>Layer</th>
                        <th>Description</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        { s: "Bronze", d: "Raw ingestion layer. Original data from Olist sources with minimal cleaning." },
                        { s: "Silver", d: "Cleaned and standardized layer. Deduplicated, typed, and structured for analysis." },
                        { s: "Gold", d: "Business logic layer. Aggregated metrics, dimensional modeling, and high-level KPIs." },
                        { s: "Semantic", d: "Analytical views. Optimized for fast querying and natural language processing." },
                        { s: "Ops", d: "System metadata. Tracking ingestion logs, health checks, and data quality metrics." }
                      ].map((item, i) => (
                        <tr key={i}>
                          <td style={{ fontWeight: 700, color: TOKENS.accent }}>{item.s}</td>
                          <td>{item.d}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Box>
                  <Typography variant="caption" sx={{ opacity: 0.4, fontStyle: 'italic' }}>
                    * The analyst agent autonomously routes queries to the most appropriate layer.
                  </Typography>
                </Box>
              ) : (
                <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.2 }}>
                  <Typography variant="body2" sx={{ fontStyle: 'italic' }}>Raw data records will appear here.</Typography>
                </Box>
              )}
            </Box>

            <Box sx={{ pt: 2, borderTop: `1px solid ${alpha("#fff", 0.05)}` }}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <TextField
                  fullWidth
                  multiline
                  maxRows={4}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask a question..."
                  variant="standard"
                  slotProps={{
                    input: { disableUnderline: true }
                  }}
                  sx={{
                    "& .MuiInputBase-root": {
                      p: 2,
                      bgcolor: alpha("#000", 0.3),
                      borderRadius: 4,
                      border: `1px solid ${alpha("#fff", 0.1)}`,
                      fontSize: "0.9rem",
                      "&.Mui-focused": { borderColor: TOKENS.accent, bgcolor: alpha("#000", 0.5) }
                    }
                  }}
                />
                <Button
                  variant="contained"
                  onClick={handleSubmit}
                  disabled={loading || !query.trim()}
                  sx={{
                    minWidth: 56, borderRadius: 4,
                    bgcolor: TOKENS.accent, color: "#000",
                    "&:hover": { bgcolor: "#d8b4fe" }
                  }}
                >
                  {loading ? <CircularProgress size={20} color="inherit" /> : "↑"}
                </Button>
              </Box>
            </Box>
          </Paper>
        </Box>
      </Box>

      <style jsx global>{`
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: rgba(168, 85, 247, 0.15); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(168, 85, 247, 0.4); }
        .markdownSummary table { display: none; }
      `}</style>
    </ThemeProvider>
  );
}
