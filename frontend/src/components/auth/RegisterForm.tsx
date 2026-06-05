import React, { useState } from 'react';
import { TextField, Button, Box, Typography, Alert, CircularProgress } from '@mui/material';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { registerSchema } from '../../utils/validators';
import type { RegisterData } from '../../types';

interface Props {
  onSubmit: (data: RegisterData) => Promise<void>;
  loading: boolean;
}

export default function RegisterForm({ onSubmit, loading }: Props) {
  const [error, setError] = useState<string | null>(null);
  const { register, handleSubmit, watch, formState: { errors } } = useForm<RegisterData & { confirmPassword: string }>({
    resolver: yupResolver(registerSchema),
  });

  const password = watch('password', '');
  const getStrength = (p: string): { label: string; color: string } => {
    if (p.length < 8) return { label: 'Weak', color: '#F44336' };
    if (!/[A-Z]/.test(p) || !/[a-z]/.test(p) || !/\d/.test(p))
      return { label: 'Medium', color: '#FF9800' };
    return { label: 'Strong', color: '#4CAF50' };
  };
  const strength = getStrength(password);

  const handleFormSubmit = async (data: RegisterData & { confirmPassword: string }) => {
    setError(null);
    try {
      await onSubmit(data);
    } catch (e: any) {
      setError(e?.message || 'Registration failed');
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit(handleFormSubmit)} noValidate>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <TextField fullWidth label="Full Name" {...register('full_name')} margin="normal" />
      <TextField
        fullWidth label="Email" {...register('email')}
        error={!!errors.email} helperText={errors.email?.message}
        margin="normal" autoComplete="email"
      />
      <TextField
        fullWidth label="Username" {...register('username')}
        error={!!errors.username} helperText={errors.username?.message}
        margin="normal" autoComplete="username"
      />
      <TextField
        fullWidth label="Password" type="password" {...register('password')}
        error={!!errors.password} helperText={errors.password?.message}
        margin="normal" autoComplete="new-password"
      />
      {password.length > 0 && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
          <Typography variant="caption">Strength:</Typography>
          <Box sx={{ flexGrow: 1, height: 4, bgcolor: '#e0e0e0', borderRadius: 2 }}>
            <Box
              sx={{
                width: password.length < 8 ? '33%' : password.length < 12 ? '66%' : '100%',
                height: '100%',
                bgcolor: strength.color,
                borderRadius: 2,
                transition: 'all 0.3s',
              }}
            />
          </Box>
          <Typography variant="caption" sx={{ color: strength.color, fontWeight: 600 }}>
            {strength.label}
          </Typography>
        </Box>
      )}
      <Button
        type="submit" fullWidth variant="contained" size="large"
        disabled={loading} sx={{ mt: 3, mb: 2, py: 1.5 }}
      >
        {loading ? <CircularProgress size={24} /> : 'Create Account'}
      </Button>
    </Box>
  );
}
