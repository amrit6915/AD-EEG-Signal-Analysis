import React, { useState } from 'react';
import {
  Box, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, Chip, IconButton, Button, TableSortLabel,
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import DeleteIcon from '@mui/icons-material/Delete';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getDetectionHistory, getResultDetail, deleteResult } from '../services/detectionService';
import type { DetectionHistoryItem, DetectionResult } from '../types';
import { formatDate, formatProbability } from '../utils/formatters';
import Pagination from '../components/common/Pagination';
import Modal from '../components/common/Modal';
import Loading from '../components/Loading';

export default function ResultsPage() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [selectedResult, setSelectedResult] = useState<DetectionResult | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['history', page],
    queryFn: () => getDetectionHistory({ page, limit: 20 }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteResult,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['history'] }),
  });

  const handleView = async (id: string) => {
    setDetailLoading(true);
    setDetailOpen(true);
    try {
      const result = await getResultDetail(id);
      setSelectedResult(result);
    } catch {
      setSelectedResult(null);
    }
    setDetailLoading(false);
  };

  if (isLoading) return <Loading />;

  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>Detection Results</Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        View and manage all detection history
      </Typography>

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><b>Date</b></TableCell>
                <TableCell><b>Status</b></TableCell>
                <TableCell><b>EDF File</b></TableCell>
                <TableCell><b>Result</b></TableCell>
                <TableCell><b>Max Probability</b></TableCell>
                <TableCell><b>Actions</b></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data?.detections?.map((d: DetectionHistoryItem) => (
                <TableRow key={d.id} hover>
                  <TableCell>{d.started_at ? formatDate(d.started_at) : '-'}</TableCell>
                  <TableCell>
                    <Chip
                      label={d.status}
                      color={d.status === 'completed' ? 'success' : d.status === 'failed' ? 'error' : 'warning'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{d.edf_filename || '-'}</TableCell>
                  <TableCell>
                    {d.status === 'completed' ? (
                      <Chip
                        label={d.seizure_detected ? 'Seizure' : 'Normal'}
                        color={d.seizure_detected ? 'error' : 'success'}
                        size="small"
                        variant="outlined"
                      />
                    ) : '-'}
                  </TableCell>
                  <TableCell>{d.max_probability ? formatProbability(d.max_probability) : '-'}</TableCell>
                  <TableCell>
                    <IconButton size="small" onClick={() => handleView(d.id)} color="primary">
                      <VisibilityIcon />
                    </IconButton>
                    <IconButton size="small" onClick={() => deleteMutation.mutate(d.id)} color="error">
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {(!data?.detections || data.detections.length === 0) && (
                <TableRow>
                  <TableCell colSpan={6} align="center">No detection results found</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <Box sx={{ p: 2 }}>
          <Pagination
            page={page}
            totalPages={data?.total_pages || 1}
            total={data?.total || 0}
            onChange={setPage}
          />
        </Box>
      </Paper>

      <Modal open={detailOpen} onClose={() => setDetailOpen(false)} title="Detection Details" maxWidth="md">
        {detailLoading ? (
          <Loading message="Loading details..." />
        ) : selectedResult ? (
          <Box>
            <Typography variant="subtitle1" fontWeight={600} gutterBottom>
              Seizure {selectedResult.summary?.seizure_detected ? 'Detected' : 'Not Detected'}
              {' | '}Max Probability: {selectedResult.summary?.max_probability ? formatProbability(selectedResult.summary.max_probability) : 'N/A'}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Windows: {selectedResult.summary?.total_windows} | Peaks: {selectedResult.summary?.num_peaks}
            </Typography>
            {selectedResult.visualization_data && (
              <Box sx={{ mt: 2 }}>
                <img
                  src={`data:image/png;base64,${selectedResult.visualization_data}`}
                  alt="Detection"
                  style={{ width: '100%', borderRadius: 8 }}
                />
              </Box>
            )}
            <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
              <Button
                variant="outlined" size="small"
                onClick={() => {
                  const dataStr = JSON.stringify(selectedResult, null, 2);
                  const blob = new Blob([dataStr], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url; a.download = `result_${selectedResult.id}.json`;
                  a.click();
                }}
              >
                Export JSON
              </Button>
            </Box>
          </Box>
        ) : (
          <Typography color="text.secondary">Failed to load details</Typography>
        )}
      </Modal>
    </Box>
  );
}
