import React from 'react';
import { Box, Paper, Typography, Link } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import RegisterForm from '../components/auth/RegisterForm';
import { useAuth } from '../hooks/useAuth';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { registerUser, loading } = useAuth();

  return (
    <Box display="flex" alignItems="center" justifyContent="center" minHeight="100vh" bgcolor="#F5F5F5">
      <Paper elevation={3} sx={{ p: 4, maxWidth: 480, width: '100%', mx: 2 }}>
        <Typography variant="h4" align="center" fontWeight={700} gutterBottom>
          Create Account
        </Typography>
        <Typography variant="body2" align="center" color="text.secondary" sx={{ mb: 3 }}>
          Register for EEG Seizure Detection
        </Typography>
        <RegisterForm onSubmit={registerUser} loading={loading} />
        <Typography align="center" variant="body2" sx={{ mt: 2 }}>
          Already have an account?{' '}
          <Link component="button" variant="body2" onClick={() => navigate('/login')} fontWeight={600}>
            Sign in
          </Link>
        </Typography>
      </Paper>
    </Box>
  );
}
