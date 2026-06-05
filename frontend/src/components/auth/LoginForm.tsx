import React, { useState } from 'react';
import { TextField, Button, Box, Typography, Alert, CircularProgress } from '@mui/material';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { loginSchema } from '../../utils/validators';
import type { LoginCredentials } from '../../types';

interface Props {
  onSubmit: (data: LoginCredentials) => Promise<void>;
  loading: boolean;
}

export default function LoginForm({ onSubmit, loading }: Props) {
  const [error, setError] = useState<string | null>(null);
  const { register, handleSubmit, formState: { errors } } = useForm<LoginCredentials>({
    resolver: yupResolver(loginSchema),
  });

  const handleFormSubmit = async (data: LoginCredentials) => {
    setError(null);
    try {
      await onSubmit(data);
    } catch (e: any) {
      setError(e?.message || 'Login failed');
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit(handleFormSubmit)} noValidate>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <TextField
        fullWidth
        label="Email"
        {...register('email')}
        error={!!errors.email}
        helperText={errors.email?.message}
        margin="normal"
        autoComplete="email"
      />
      <TextField
        fullWidth
        label="Password"
        type="password"
        {...register('password')}
        error={!!errors.password}
        helperText={errors.password?.message}
        margin="normal"
        autoComplete="current-password"
      />
      <Button
        type="submit"
        fullWidth
        variant="contained"
        size="large"
        disabled={loading}
        sx={{ mt: 3, mb: 2, py: 1.5 }}
      >
        {loading ? <CircularProgress size={24} /> : 'Sign In'}
      </Button>
    </Box>
  );
}
