import React from 'react';
import { Box, Paper, Typography, Link } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../components/auth/LoginForm';
import { useAuth } from '../hooks/useAuth';

export default function LoginPage() {
  const navigate = useNavigate();
  const { loginUser, loading } = useAuth();

  return (
    <Box display="flex" alignItems="center" justifyContent="center" minHeight="100vh" bgcolor="#F5F5F5">
      <Paper elevation={3} sx={{ p: 4, maxWidth: 420, width: '100%', mx: 2 }}>
        <Typography variant="h4" align="center" fontWeight={700} gutterBottom>
          Welcome Back
        </Typography>
        <Typography variant="body2" align="center" color="text.secondary" sx={{ mb: 3 }}>
          Sign in to your EEG Seizure Detection account
        </Typography>
        <LoginForm onSubmit={loginUser} loading={loading} />
        <Typography align="center" variant="body2">
          Don't have an account?{' '}
          <Link component="button" variant="body2" onClick={() => navigate('/register')} fontWeight={600}>
            Sign up
          </Link>
        </Typography>
      </Paper>
    </Box>
  );
}
