import React, { useState, useEffect, useCallback } from 'react';
import {
  Box, Paper, Typography, Grid, Button, Slider, FormControl, InputLabel,
  Select, MenuItem, CircularProgress, Alert, Card, CardContent, Chip,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { useQuery, useMutation } from '@tanstack/react-query';
import { getFiles } from '../services/fileService';
import { startDetection, getDetectionStatus, getDetectionResults } from '../services/detectionService';
import type { FileRecord, DetectionResult } from '../types';
import { formatProbability } from '../utils/formatters';
import Loading from '../components/Loading';

export default function DetectionPage() {
  const [edfFileId, setEdfFileId] = useState('');
  const [seizuresFileId, setSeizuresFileId] = useState('');
  const [threshold, setThreshold] = useState(0.5);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { data: edfFiles, isLoading: edfLoading } = useQuery({
    queryKey: ['files', 'edf'],
    queryFn: () => getFiles({ file_type: 'edf', limit: 100 }),
  });

  const { data: seizuresFiles, isLoading: szLoading } = useQuery({
    queryKey: ['files', 'seizures'],
    queryFn: () => getFiles({ file_type: 'seizures', limit: 100 }),
  });

  const detectionMutation = useMutation({
    mutationFn: () => startDetection(edfFileId, seizuresFileId, threshold),
    onSuccess: (data) => {
      setTaskId(data.task_id);
      setStatus('pending');
      setProgress(0);
      setError(null);
    },
    onError: (e: any) => setError(e?.message || 'Detection failed to start'),
  });

  useEffect(() => {
    if (!taskId || status === 'completed' || status === 'failed') return;

    const interval = setInterval(async () => {
      try {
        const s = await getDetectionStatus(taskId);
        setStatus(s.status);
        setProgress(s.progress);

        if (s.status === 'completed') {
          clearInterval(interval);
          const r = await getDetectionResults(taskId);
          setResult(r);
        } else if (s.status === 'failed') {
          clearInterval(interval);
          setError('Detection processing failed');
        }
      } catch {
        clearInterval(interval);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [taskId, status]);

  const handleStart = () => {
    if (!edfFileId || !seizuresFileId) {
      setError('Please select both EDF and seizures files');
      return;
    }
    setResult(null);
    setError(null);
    detectionMutation.mutate();
  };

  const isProcessing = status === 'pending' || status === 'processing';

  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>Seizure Detection</Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Select files and configure detection parameters
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>Detection Configuration</Typography>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>EDF File</InputLabel>
              <Select value={edfFileId} label="EDF File" onChange={(e) => setEdfFileId(e.target.value)} disabled={isProcessing}>
                {edfFiles?.files?.map((f: FileRecord) => (
                  <MenuItem key={f.id} value={f.id}>{f.original_filename}</MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Seizures File</InputLabel>
              <Select value={seizuresFileId} label="Seizures File" onChange={(e) => setSeizuresFileId(e.target.value)} disabled={isProcessing}>
                {seizuresFiles?.files?.map((f: FileRecord) => (
                  <MenuItem key={f.id} value={f.id}>{f.original_filename}</MenuItem>
                ))}
              </Select>
            </FormControl>

            <Typography gutterBottom>Detection Threshold: {threshold.toFixed(2)}</Typography>
            <Slider
              value={threshold} onChange={(_, v) => setThreshold(v as number)}
              min={0} max={1} step={0.05}
              disabled={isProcessing}
              sx={{ mb: 2 }}
            />

            <Button
              variant="contained" size="large" fullWidth
              startIcon={isProcessing ? <CircularProgress size={20} /> : <PlayArrowIcon />}
              onClick={handleStart}
              disabled={isProcessing || !edfFileId || !seizuresFileId}
            >
              {isProcessing ? 'Processing...' : 'Start Detection'}
            </Button>

            {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}

            {isProcessing && (
              <Box sx={{ mt: 2, textAlign: 'center' }}>
                <CircularProgress variant="determinate" value={progress} size={60} />
                <Typography variant="body2" sx={{ mt: 1 }}>Status: {status}</Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={7}>
          {result ? (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight={600} gutterBottom>Detection Results</Typography>

              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6} md={3}>
                  <Card>
                    <CardContent sx={{ textAlign: 'center', py: 2 }}>
                      <Chip
                        label={result.summary.seizure_detected ? 'Seizure Detected' : 'No Seizure'}
                        color={result.summary.seizure_detected ? 'error' : 'success'}
                        size="small"
                        sx={{ mb: 1 }}
                      />
                      <Typography variant="body2" color="text.secondary">Status</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Card>
                    <CardContent sx={{ textAlign: 'center', py: 2 }}>
                      <Typography variant="h5" fontWeight={700} color="primary">
                        {formatProbability(result.summary.max_probability)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">Max Probability</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Card>
                    <CardContent sx={{ textAlign: 'center', py: 2 }}>
                      <Typography variant="h5" fontWeight={700} color="secondary">
                        {result.summary.num_peaks}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">Peaks Found</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Card>
                    <CardContent sx={{ textAlign: 'center', py: 2 }}>
                      <Typography variant="h5" fontWeight={700}>
                        {result.summary.total_windows}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">Windows</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {result.visualization_data && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle1" fontWeight={500} gutterBottom>Visualization</Typography>
                  <img
                    src={`data:image/png;base64,${result.visualization_data}`}
                    alt="Detection Visualization"
                    style={{ width: '100%', borderRadius: 8, border: '1px solid #e0e0e0' }}
                  />
                </Box>
              )}
            </Paper>
          ) : (
            <Paper sx={{ p: 6, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                Select files and click "Start Detection"
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Results will appear here after processing
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}
