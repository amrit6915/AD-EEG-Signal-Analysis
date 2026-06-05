import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

export default function NotFoundPage() {
  const navigate = useNavigate();
  return (
    <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="100vh">
      <Typography variant="h1" fontWeight={700} color="primary">404</Typography>
      <Typography variant="h5" gutterBottom>Page Not Found</Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        The page you're looking for doesn't exist.
      </Typography>
      <Button variant="contained" onClick={() => navigate('/dashboard')}>
        Go to Dashboard
      </Button>
    </Box>
  );
}
