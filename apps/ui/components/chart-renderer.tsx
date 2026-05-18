'use client';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area, ScatterChart, Scatter } from 'recharts';
import { Box, Typography } from '@mui/material';

const COLORS = ['#b967ff', '#8884d8', '#82ca9d', '#ffc658', '#ff7300'];

export function ChartRenderer({ chartData }: { chartData: any }) {
  if (!chartData || !chartData.data || chartData.data.length === 0) return null;

  const { type, title, xAxisKey, yAxisKey, data } = chartData;

  const renderChartType = () => {
    switch (type) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey={xAxisKey} stroke="#d0d0d0" tick={{ fill: '#d0d0d0' }} />
              <YAxis stroke="#d0d0d0" tick={{ fill: '#d0d0d0' }} />
              <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', borderColor: '#b967ff', color: '#fff' }} />
              <Legend wrapperStyle={{ color: '#d0d0d0' }} />
              <Line type="monotone" dataKey={yAxisKey} stroke="#b967ff" activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        );
      case 'pie':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data} dataKey={yAxisKey} nameKey={xAxisKey} cx="50%" cy="50%" outerRadius={100} label={{ fill: '#fff' }}>
                {data.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', borderColor: '#b967ff', color: '#fff' }} />
              <Legend wrapperStyle={{ color: '#d0d0d0' }} />
            </PieChart>
          </ResponsiveContainer>
        );
      case 'area':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey={xAxisKey} stroke="#d0d0d0" tick={{ fill: '#d0d0d0' }} />
              <YAxis stroke="#d0d0d0" tick={{ fill: '#d0d0d0' }} />
              <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', borderColor: '#b967ff', color: '#fff' }} />
              <Legend wrapperStyle={{ color: '#d0d0d0' }} />
              <Area type="monotone" dataKey={yAxisKey} stroke="#b967ff" fill="#b967ff" fillOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
        );
      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey={xAxisKey} type="category" stroke="#d0d0d0" tick={{ fill: '#d0d0d0' }} />
              <YAxis dataKey={yAxisKey} type="number" stroke="#d0d0d0" tick={{ fill: '#d0d0d0' }} />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1a1a2e', borderColor: '#b967ff', color: '#fff' }} />
              <Legend wrapperStyle={{ color: '#d0d0d0' }} />
              <Scatter name={title || 'Data'} data={data} fill="#b967ff" />
            </ScatterChart>
          </ResponsiveContainer>
        );
      case 'bar':
      default:
        return (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey={xAxisKey} stroke="#d0d0d0" tick={{ fill: '#d0d0d0' }} />
              <YAxis stroke="#d0d0d0" tick={{ fill: '#d0d0d0' }} />
              <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', borderColor: '#b967ff', color: '#fff' }} cursor={{fill: 'rgba(255,255,255,0.05)'}} />
              <Legend wrapperStyle={{ color: '#d0d0d0' }} />
              <Bar dataKey={yAxisKey} fill="#b967ff" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        );
    }
  };

  return (
    <Box sx={{ mt: 1, mb: 1, p: 2, border: '1px solid rgba(255,255,255,0.1)', borderRadius: 2, bgcolor: 'rgba(0,0,0,0.2)', flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      {title && <Typography variant="subtitle1" sx={{ color: '#fff', mb: 1, textAlign: 'center', fontWeight: 'bold' }}>{title}</Typography>}
      <Box sx={{ flex: 1, minHeight: 0 }}>
        {renderChartType()}
      </Box>
    </Box>
  );
}