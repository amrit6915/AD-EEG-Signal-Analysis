import React, { useState } from 'react';
import { Box, Paper, Typography, Grid, ToggleButton, ToggleButtonGroup, Card, CardContent } from '@mui/material';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Area, AreaChart,
} from 'recharts';
import { useQuery } from '@tanstack/react-query';
import { getDashboard, getTrends } from '../services/detectionService';
import Loading from '../components/Loading';
import { formatProbability } from '../utils/formatters';

export default function AnalyticsPage() {
  const [range, setRange] = useState('30d');

  const { data: dashboard, isLoading: dashLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboard,
  });

  const { data: trends, isLoading: trendLoading } = useQuery({
    queryKey: ['trends', range],
    queryFn: () => getTrends(range),
  });

  if (dashLoading || trendLoading) return <Loading />;

  const chartData = trends?.dates?.map((date, i) => ({
    date,
    detections: trends.detection_counts[i],
    seizures: trends.seizure_counts[i],
    avgProb: trends.avg_probabilities[i] ? (trends.avg_probabilities[i] * 100).toFixed(1) : 0,
  })) || [];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700}>Analytics</Typography>
        <ToggleButtonGroup value={range} exclusive onChange={(_, v) => v && setRange(v)} size="small">
          <ToggleButton value="7d">7 days</ToggleButton>
          <ToggleButton value="30d">30 days</ToggleButton>
          <ToggleButton value="90d">90 days</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={6} md={3}>
          <Card><CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" fontWeight={700} color="primary">{dashboard?.total_detections || 0}</Typography>
            <Typography variant="body2" color="text.secondary">Total Detections</Typography>
          </CardContent></Card>
        </Grid>
        <Grid item xs={6} md={3}>
          <Card><CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" fontWeight={700} color="secondary">{dashboard?.seizures_detected || 0}</Typography>
            <Typography variant="body2" color="text.secondary">Seizures Found</Typography>
          </CardContent></Card>
        </Grid>
        <Grid item xs={6} md={3}>
          <Card><CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" fontWeight={700} color="success.main">{dashboard?.detection_rate || 0}%</Typography>
            <Typography variant="body2" color="text.secondary">Detection Rate</Typography>
          </CardContent></Card>
        </Grid>
        <Grid item xs={6} md={3}>
          <Card><CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" fontWeight={700}>{dashboard?.avg_probability ? formatProbability(dashboard.avg_probability) : '0%'}</Typography>
            <Typography variant="body2" color="text.secondary">Avg Probability</Typography>
          </CardContent></Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>Detections Over Time</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="detections" fill="#1976D2" radius={[4, 4, 0, 0]} name="Detections" />
                <Bar dataKey="seizures" fill="#DC004E" radius={[4, 4, 0, 0]} name="Seizures" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>Detection Rate Trend</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="detections" stroke="#1976D2" fill="#1976D2" fillOpacity={0.1} name="Detections" />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>Average Probability Trend</Typography>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
                <Tooltip formatter={(v: number) => `${v}%`} />
                <Line type="monotone" dataKey="avgProb" stroke="#FF9800" strokeWidth={2} dot={false} name="Avg Probability" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
