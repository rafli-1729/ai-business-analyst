'use client';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area,
  ComposedChart, ScatterChart, Scatter
} from 'recharts';
import { Box, Typography } from '@mui/material';

const COLORS = ['#b967ff', '#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

const formatNumber = (val: any) => {
  if (typeof val !== 'number') return val;
  if (Number.isInteger(val)) return val;
  if (val > 1000000) return (val / 1000000).toFixed(1) + 'M';
  if (val > 1000) return (val / 1000).toFixed(1) + 'k';
  return Number(val.toFixed(2));
};

export function ChartRenderer({ chartData }: { chartData: any }) {
  if (!chartData || !chartData.data || chartData.data.length === 0) return null;

  const { type, title, xAxisKey, yAxisKey, data } = chartData;
  const isMulti = Array.isArray(yAxisKey);
  const keys = isMulti ? yAxisKey : [yAxisKey];

  const renderChartType = () => {
    switch (type) {
      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis 
                type="number" 
                dataKey={xAxisKey} 
                name={xAxisKey} 
                stroke="#888" 
                tick={{ fill: '#888', fontSize: 11 }} 
                tickFormatter={formatNumber}
              />
              <YAxis 
                type="number" 
                dataKey={keys[0]} 
                name={keys[0]} 
                stroke="#888" 
                tick={{ fill: '#888', fontSize: 11 }} 
                tickFormatter={formatNumber}
              />
              <Tooltip 
                cursor={{ strokeDasharray: '3 3' }}
                contentStyle={{ backgroundColor: '#1a1a2e', borderColor: '#b967ff', color: '#fff', borderRadius: '8px' }} 
              />
              <Scatter name={title} data={data} fill="#b967ff" />
            </ScatterChart>
          </ResponsiveContainer>
        );
      case 'composed':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey={xAxisKey} stroke="#888" tick={{ fill: '#888', fontSize: 11 }} />
              <YAxis yAxisId="left" stroke="#888" tick={{ fill: '#888', fontSize: 11 }} tickFormatter={formatNumber} />
              <YAxis yAxisId="right" orientation="right" stroke="#888" tick={{ fill: '#888', fontSize: 11 }} tickFormatter={formatNumber} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1a1a2e', borderColor: '#b967ff', color: '#fff', borderRadius: '8px' }} 
                formatter={(value, name) => [formatNumber(value), name]}
              />
              <Legend wrapperStyle={{ paddingTop: '15px', color: '#888', fontSize: '12px' }} />
              <Bar yAxisId="left" dataKey={keys[0]} fill={COLORS[0]} radius={[4, 4, 0, 0]} barSize={30} />
              {keys.length > 1 && (
                <Line yAxisId="right" type="monotone" dataKey={keys[1]} stroke={COLORS[2]} strokeWidth={3} dot={{ r: 4 }} />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        );
      case 'line':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey={xAxisKey} stroke="#888" tick={{ fill: '#888', fontSize: 11 }} />
              <YAxis stroke="#888" tick={{ fill: '#888', fontSize: 11 }} tickFormatter={formatNumber} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1a1a2e', borderColor: '#b967ff', color: '#fff', borderRadius: '8px' }} 
                formatter={(value, name) => [formatNumber(value), name]}
              />
              <Legend wrapperStyle={{ paddingTop: '15px', color: '#888', fontSize: '12px' }} />
              {keys.map((key: string, idx: number) => (
                <Line 
                  key={key}
                  type="monotone" 
                  dataKey={key} 
                  stroke={COLORS[idx % COLORS.length]} 
                  strokeWidth={3} 
                  dot={{ r: 3, fill: COLORS[idx % COLORS.length] }} 
                  activeDot={{ r: 6 }} 
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        );
      case 'pie':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie 
                data={data} 
                dataKey={keys[0]} 
                nameKey={xAxisKey} 
                cx="45%" 
                cy="50%" 
                innerRadius="55%"
                outerRadius="75%" 
                paddingAngle={4}
                label={false}
              >
                {data.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: '#1a1a2e', borderColor: '#b967ff', color: '#fff', borderRadius: '8px' }} 
                formatter={(value) => [formatNumber(value), 'Value']}
              />
              <Legend 
                layout="vertical" 
                verticalAlign="middle" 
                align="right" 
                wrapperStyle={{ color: '#888', paddingLeft: '15px', fontSize: '11px' }} 
              />
            </PieChart>
          </ResponsiveContainer>
        );
      case 'area':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey={xAxisKey} stroke="#888" tick={{ fill: '#888', fontSize: 11 }} />
              <YAxis stroke="#888" tick={{ fill: '#888', fontSize: 11 }} tickFormatter={formatNumber} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1a1a2e', borderColor: '#b967ff', color: '#fff', borderRadius: '8px' }} 
                formatter={(value, name) => [formatNumber(value), name]}
              />
              <Legend wrapperStyle={{ paddingTop: '15px', color: '#888', fontSize: '12px' }} />
              {keys.map((key: string, idx: number) => (
                <Area 
                  key={key}
                  type="monotone" 
                  dataKey={key} 
                  stroke={COLORS[idx % COLORS.length]} 
                  fill={COLORS[idx % COLORS.length]} 
                  fillOpacity={0.2} 
                />
              ))}
            </AreaChart>
          </ResponsiveContainer>
        );
      case 'bar':
      default:
        return (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey={xAxisKey} stroke="#888" tick={{ fill: '#888', fontSize: 11 }} />
              <YAxis stroke="#888" tick={{ fill: '#888', fontSize: 11 }} tickFormatter={formatNumber} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1a1a2e', borderColor: '#b967ff', color: '#fff', borderRadius: '8px' }} 
                cursor={{fill: 'rgba(255,255,255,0.02)'}}
                formatter={(value, name) => [formatNumber(value), name]}
              />
              <Legend wrapperStyle={{ paddingTop: '15px', color: '#888', fontSize: '12px' }} />
              {keys.map((key: string, idx: number) => (
                <Bar 
                  key={key}
                  dataKey={key} 
                  fill={COLORS[idx % COLORS.length]} 
                  radius={[4, 4, 0, 0]} 
                  barSize={isMulti ? undefined : 35} 
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        );
    }
  };

  return (
    <Box sx={{ mt: 0, mb: 0, p: 1, flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, overflow: 'hidden' }}>
      {title && (
        <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.5)', mb: 1, textAlign: 'center', fontWeight: 600, letterSpacing: 0.8, fontSize: '0.75rem' }}>
          {title.toUpperCase()}
        </Typography>
      )}
      <Box sx={{ flex: 1, minHeight: 0, width: '100%' }}>
        {renderChartType()}
      </Box>
    </Box>
  );
}
