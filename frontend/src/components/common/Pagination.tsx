import React from 'react';
import { Box, Pagination as MuiPagination, Typography } from '@mui/material';

interface Props {
  page: number;
  totalPages: number;
  total: number;
  onChange: (page: number) => void;
}

export default function Pagination({ page, totalPages, total, onChange }: Props) {
  if (totalPages <= 1) return null;
  return (
    <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
      <Typography variant="body2" color="text.secondary">
        Total: {total} items
      </Typography>
      <MuiPagination
        count={totalPages}
        page={page}
        onChange={(_, p) => onChange(p)}
        color="primary"
        shape="rounded"
      />
    </Box>
  );
}
