import React, { useState, useCallback } from 'react';
import {
  Box, Paper, Typography, Button, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, IconButton, Chip, LinearProgress, Alert,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DeleteIcon from '@mui/icons-material/Delete';
import DownloadIcon from '@mui/icons-material/Download';
import { useDropzone } from 'react-dropzone';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getFiles, uploadFile, deleteFile, downloadFile } from '../services/fileService';
import type { FileRecord } from '../types';
import { formatFileSize, formatDate } from '../utils/formatters';
import Pagination from '../components/common/Pagination';
import { useAppDispatch } from '../store/hooks';
import { addToast } from '../store/slices/uiSlice';

export default function FileManagementPage() {
  const dispatch = useAppDispatch();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const { data, isLoading } = useQuery({
    queryKey: ['files', page],
    queryFn: () => getFiles({ page, limit: 20 }),
  });

  const uploadMutation = useMutation({
    mutationFn: async ({ file, type }: { file: File; type: 'edf' | 'seizures' }) => {
      return uploadFile(file, type);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files'] });
      dispatch(addToast({ message: 'File uploaded successfully', severity: 'success' }));
    },
    onError: (e: any) => {
      dispatch(addToast({ message: e?.message || 'Upload failed', severity: 'error' }));
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteFile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files'] });
      dispatch(addToast({ message: 'File deleted', severity: 'info' }));
    },
  });

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true);
    for (let i = 0; i < acceptedFiles.length; i++) {
      const file = acceptedFiles[i];
      const ext = file.name.split('.').pop()?.toLowerCase();
      const type = ext === 'edf' ? 'edf' : ext === 'seizures' ? 'seizures' : null;
      if (!type) {
        dispatch(addToast({ message: `Invalid file type: ${file.name}`, severity: 'warning' }));
        continue;
      }
      setUploadProgress(Math.round(((i + 1) / acceptedFiles.length) * 100));
      uploadMutation.mutate({ file, type });
    }
    setUploading(false);
    setUploadProgress(0);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/octet-stream': ['.edf'],
      'text/plain': ['.seizures'],
    },
    maxSize: 500 * 1024 * 1024,
  });

  const handleDownload = async (fileId: string, filename: string) => {
    try {
      const blob = await downloadFile(fileId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = filename;
      a.click();
    } catch {
      dispatch(addToast({ message: 'Download failed', severity: 'error' }));
    }
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>File Management</Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Upload and manage EDF and seizures annotation files
      </Typography>

      <Paper
        {...getRootProps()}
        sx={{
          p: 4, mb: 3, textAlign: 'center', cursor: 'pointer',
          border: '2px dashed', borderColor: isDragActive ? 'primary.main' : '#ccc',
          bgcolor: isDragActive ? 'action.hover' : 'background.paper',
          transition: 'all 0.3s',
        }}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Supported: .edf and .seizures files (max 500MB)
        </Typography>
      </Paper>

      {uploading && <LinearProgress variant="determinate" value={uploadProgress} sx={{ mb: 2 }} />}

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><b>Filename</b></TableCell>
                <TableCell><b>Type</b></TableCell>
                <TableCell><b>Size</b></TableCell>
                <TableCell><b>Uploaded</b></TableCell>
                <TableCell><b>Actions</b></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data?.files?.map((f: FileRecord) => (
                <TableRow key={f.id} hover>
                  <TableCell>{f.original_filename}</TableCell>
                  <TableCell>
                    <Chip label={f.file_type} size="small" color={f.file_type === 'edf' ? 'primary' : 'secondary'} variant="outlined" />
                  </TableCell>
                  <TableCell>{formatFileSize(f.file_size)}</TableCell>
                  <TableCell>{formatDate(f.uploaded_at)}</TableCell>
                  <TableCell>
                    <IconButton size="small" onClick={() => handleDownload(f.id, f.original_filename)} color="primary">
                      <DownloadIcon />
                    </IconButton>
                    <IconButton size="small" onClick={() => deleteMutation.mutate(f.id)} color="error">
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {(!data?.files || data.files.length === 0) && (
                <TableRow><TableCell colSpan={5} align="center">No files uploaded yet</TableCell></TableRow>
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
    </Box>
  );
}
