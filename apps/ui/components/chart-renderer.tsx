'use client';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area,
  ComposedChart, ScatterChart, Scatter
} from 'recharts';
import { Box, Typography, alpha } from '@mui/material';

const COLORS = ['#c084fc', '#818cf8', '#2dd4bf', '#fbbf24', '#f87171', '#60a5fa', '#34d399', '#f472b6', '#a78bfa'];
const ACCENT_COLOR = '#c084fc';

const formatNumber = (val: any) => {
// ...

  if (typeof val !== 'number') return val;
  if (Number.isInteger(val)) return val;
  if (val > 1000000) return (val / 1000000).toFixed(1) + 'M';
  if (val > 1000) return (val / 1000).toFixed(1) + 'k';
  return Number(val.toFixed(2));
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <Box sx={{ 
        bgcolor: 'rgba(10, 11, 15, 0.95)', 
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(192, 132, 252, 0.4)',
        p: 2,
        borderRadius: '12px',
        boxShadow: '0 10px 40px rgba(0,0,0,0.6)',
        display: 'flex',
        flexDirection: 'column',
        gap: 1
      }}>
        <Typography variant="caption" sx={{ color: '#c084fc', fontWeight: 800, textTransform: 'uppercase', letterSpacing: 1 }}>
          {label}
        </Typography>
        <Divider sx={{ borderColor: 'rgba(255,255,255,0.05)', my: 0.5 }} />
        {payload.map((p: any, i: number) => (
          <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: p.color || p.fill }} />
            <Typography variant="body2" sx={{ color: '#fff', fontWeight: 600, fontSize: '0.85rem' }}>
              {p.name}:
            </Typography>
            <Typography variant="body2" sx={{ color: '#94a3b8', ml: 'auto', fontFamily: 'monospace' }}>
              {formatNumber(p.value)}
            </Typography>
          </Box>
        ))}
      </Box>
    );
  }
  return null;
};

// Add Divider import from MUI
import { Divider } from '@mui/material';

export function ChartRenderer({ chartData }: { chartData: any }) {
  if (!chartData || !chartData.data || chartData.data.length === 0) {
    return (
      <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.3 }}>
        <Typography variant="caption">NO DATA FOR CHART</Typography>
      </Box>
    );
  }

  const { type, xAxisKey, yAxisKey, data } = chartData;
  const isMulti = Array.isArray(yAxisKey);
  const keys = isMulti ? yAxisKey : [yAxisKey];

  const renderChartType = () => {
    switch (type) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
              <XAxis dataKey={xAxisKey} stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 10 }} axisLine={false} tickLine={false} dy={10} />
              <YAxis stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={formatNumber} />
              <Tooltip content={<CustomTooltip />} />
              <Legend iconType="circle" wrapperStyle={{ fontSize: 10, paddingTop: 20 }} />
              {keys.map((key: string, idx: number) => (
                <Line key={key} type="monotone" dataKey={key} stroke={COLORS[idx % COLORS.length]} strokeWidth={3} dot={{ r: 0 }} activeDot={{ r: 6, strokeWidth: 0 }} />
              ))}
            </LineChart>
          </ResponsiveContainer>
        );
      case 'pie':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data} dataKey={keys[0]} nameKey={xAxisKey} cx="50%" cy="50%" innerRadius="60%" outerRadius="85%" paddingAngle={5}>
                {data.map((entry: any, index: number) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend iconType="circle" wrapperStyle={{ fontSize: 10 }} />
            </PieChart>
          </ResponsiveContainer>
        );
      case 'area':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
              <defs>
                {keys.map((key: string, idx: number) => (
                  <linearGradient key={`grad-${key}`} id={`grad-${key}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS[idx % COLORS.length]} stopOpacity={0.3}/>
                    <stop offset="95%" stopColor={COLORS[idx % COLORS.length]} stopOpacity={0}/>
                  </linearGradient>
                ))}
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
              <XAxis dataKey={xAxisKey} stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 10 }} axisLine={false} tickLine={false} dy={10} />
              <YAxis stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={formatNumber} />
              <Tooltip content={<CustomTooltip />} />
              <Legend iconType="circle" wrapperStyle={{ fontSize: 10, paddingTop: 20 }} />
              {keys.map((key: string, idx: number) => (
                <Area key={key} type="monotone" dataKey={key} stroke={COLORS[idx % COLORS.length]} fill={`url(#grad-${key})`} strokeWidth={3} />
              ))}
            </AreaChart>
          </ResponsiveContainer>
        );
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
              <XAxis dataKey={xAxisKey} stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 10 }} axisLine={false} tickLine={false} dy={10} />
              <YAxis stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={formatNumber} />
              <Tooltip content={<CustomTooltip />} cursor={{fill: 'rgba(255,255,255,0.05)'}} />
              <Legend iconType="circle" wrapperStyle={{ fontSize: 10, paddingTop: 20 }} />
              {keys.map((key: string, idx: number) => (
                <Bar key={key} dataKey={key} fill={COLORS[idx % COLORS.length]} radius={[6, 6, 0, 0]} barSize={isMulti ? undefined : 40} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        );
      case 'composed':
      case 'dual_axis':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
              <XAxis dataKey={xAxisKey} stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 10 }} axisLine={false} tickLine={false} dy={10} />
              <YAxis yAxisId="left" stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={formatNumber} />
              <YAxis yAxisId="right" orientation="right" stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={formatNumber} />
              <Tooltip content={<CustomTooltip />} />
              <Legend iconType="circle" wrapperStyle={{ fontSize: 10, paddingTop: 20 }} />
              <Bar yAxisId="left" dataKey={keys[0]} fill={ACCENT_COLOR} radius={[6, 6, 0, 0]} barSize={40} />
              {keys.slice(1).map((key: string, idx: number) => (
                <Line key={key} yAxisId="right" type="monotone" dataKey={key} stroke={COLORS[(idx + 1) % COLORS.length]} strokeWidth={3} dot={{ r: 4 }} />
              ))}
            </ComposedChart>
          </ResponsiveContainer>
        );
      default:
        return (
          <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.3 }}>
            <Typography variant="caption">UNKNOWN CHART TYPE</Typography>
          </Box>
        );
    }
  };

  return (
    <Box sx={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      {renderChartType()}
    </Box>
  );
}
