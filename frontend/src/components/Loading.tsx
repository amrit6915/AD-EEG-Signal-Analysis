import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

interface Props {
  message?: string;
}

export default function Loading({ message = 'Loading...' }: Props) {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="60vh"
    >
      <CircularProgress size={48} sx={{ mb: 2 }} />
      <Typography variant="body1" color="text.secondary">
        {message}
      </Typography>
    </Box>
  );
}
