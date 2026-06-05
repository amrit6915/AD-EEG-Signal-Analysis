import React from 'react';
import { Grid, Paper, Typography, Box, Card, CardContent, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line,
} from 'recharts';
import { useQuery } from '@tanstack/react-query';
import { getDashboard, getTrends } from '../services/detectionService';
import { useAuth } from '../hooks/useAuth';
import Loading from '../components/Loading';
import { formatDate, formatProbability } from '../utils/formatters';

function StatCard({ title, value, subtitle, color }: {
  title: string; value: string | number; subtitle?: string; color?: string;
}) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="body2" color="text.secondary" gutterBottom>{title}</Typography>
        <Typography variant="h4" fontWeight={700} sx={{ color: color || 'primary.main' }}>{value}</Typography>
        {subtitle && <Typography variant="caption" color="text.secondary">{subtitle}</Typography>}
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const { data: dashboard, isLoading: dashLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboard,
  });

  const { data: trends } = useQuery({
    queryKey: ['trends', '30d'],
    queryFn: () => getTrends('30d'),
  });

  if (dashLoading) return <Loading />;

  const chartData = trends?.dates?.map((date, i) => ({
    date,
    detections: trends.detection_counts[i],
    seizures: trends.seizure_counts[i],
  })) || [];

  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Welcome, {user?.full_name || user?.username}!
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        EEG Seizure Detection Dashboard
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Detections" value={dashboard?.total_detections || 0} color="#1976D2" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Seizures Detected" value={dashboard?.seizures_detected || 0} color="#DC004E" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Detection Rate" value={dashboard ? `${dashboard.detection_rate}%` : '0%'} color="#4CAF50" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Files Uploaded" value={dashboard?.total_files || 0} color="#FF9800" />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Detections (Last 30 Days)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="detections" name="Detections" fill="#1976D2" radius={[4, 4, 0, 0]} />
                <Bar dataKey="seizures" name="Seizures" fill="#DC004E" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Quick Actions
            </Typography>
            <Box display="flex" flexDirection="column" gap={2}>
              <Button variant="contained" onClick={() => navigate('/files')} fullWidth>
                Upload Files
              </Button>
              <Button variant="contained" color="secondary" onClick={() => navigate('/detection')} fullWidth>
                Run Detection
              </Button>
              <Button variant="outlined" onClick={() => navigate('/results')} fullWidth>
                View Results
              </Button>
            </Box>
          </Paper>

          {dashboard?.recent_detections && dashboard.recent_detections.length > 0 && (
            <Paper sx={{ p: 3, mt: 3 }}>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Recent Detections
              </Typography>
              {dashboard.recent_detections.slice(0, 3).map((d) => (
                <Box key={d.id} sx={{ py: 1, borderBottom: '1px solid #eee' }}>
                  <Typography variant="body2" fontWeight={500}>
                    {d.seizure_detected ? 'Seizure Detected' : 'No Seizure'} - {' '}
                    {d.max_probability ? formatProbability(d.max_probability) : 'N/A'}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatDate(d.started_at)}
                  </Typography>
                </Box>
              ))}
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}
