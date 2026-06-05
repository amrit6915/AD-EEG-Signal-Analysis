import React, { useState } from 'react';
import {
  Box, Paper, Typography, Grid, TextField, Button, Avatar, Divider,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
} from '@mui/material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getProfile, updateProfile, getLoginHistory, changePassword, deleteAccount } from '../services/authService';
import { useAuth } from '../hooks/useAuth';
import { useAppDispatch } from '../store/hooks';
import { addToast } from '../store/slices/uiSlice';
import { formatDate } from '../utils/formatters';
import Loading from '../components/Loading';

export default function ProfilePage() {
  const dispatch = useAppDispatch();
  const queryClient = useQueryClient();
  const { logoutUser } = useAuth();

  const { data: user, isLoading } = useQuery({ queryKey: ['profile'], queryFn: getProfile });
  const { data: loginHistory } = useQuery({ queryKey: ['login-history'], queryFn: getLoginHistory });

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [currentPw, setCurrentPw] = useState('');
  const [newPw, setNewPw] = useState('');

  React.useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setEmail(user.email);
    }
  }, [user]);

  const updateMutation = useMutation({
    mutationFn: () => updateProfile({ full_name: fullName, email }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] });
      dispatch(addToast({ message: 'Profile updated', severity: 'success' }));
    },
    onError: (e: any) => dispatch(addToast({ message: e?.message || 'Update failed', severity: 'error' })),
  });

  const passwordMutation = useMutation({
    mutationFn: () => changePassword(currentPw, newPw),
    onSuccess: () => {
      dispatch(addToast({ message: 'Password changed', severity: 'success' }));
      setCurrentPw(''); setNewPw('');
    },
    onError: (e: any) => dispatch(addToast({ message: e?.message || 'Password change failed', severity: 'error' })),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteAccount,
    onSuccess: () => { logoutUser(); },
  });

  if (isLoading) return <Loading />;

  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>Profile</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Avatar sx={{ width: 80, height: 80, mx: 'auto', mb: 2, bgcolor: 'secondary.main', fontSize: 32 }}>
              {(user?.full_name || user?.username || '?').charAt(0).toUpperCase()}
            </Avatar>
            <Typography variant="h6" fontWeight={600}>{user?.full_name || user?.username}</Typography>
            <Typography variant="body2" color="text.secondary">@{user?.username}</Typography>
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
              Member since {user?.created_at ? formatDate(user.created_at) : 'N/A'}
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>Edit Profile</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth label="Full Name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth label="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
              </Grid>
            </Grid>
            <Button variant="contained" onClick={() => updateMutation.mutate()} sx={{ mt: 2 }} disabled={updateMutation.isPending}>
              Save Changes
            </Button>
          </Paper>

          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>Change Password</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth label="Current Password" type="password" value={currentPw} onChange={(e) => setCurrentPw(e.target.value)} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth label="New Password" type="password" value={newPw} onChange={(e) => setNewPw(e.target.value)} />
              </Grid>
            </Grid>
            <Button variant="contained" onClick={() => passwordMutation.mutate()} sx={{ mt: 2 }} disabled={passwordMutation.isPending}>
              Change Password
            </Button>
          </Paper>

          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>Login History</Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell><b>Time</b></TableCell>
                    <TableCell><b>IP Address</b></TableCell>
                    <TableCell><b>User Agent</b></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {loginHistory?.slice(0, 10).map((h: any) => (
                    <TableRow key={h.id}>
                      <TableCell>{formatDate(h.login_time)}</TableCell>
                      <TableCell>{h.ip_address || '-'}</TableCell>
                      <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>{h.user_agent || '-'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom color="error">Danger Zone</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Delete your account and all associated data. This action cannot be undone.
            </Typography>
            <Button variant="outlined" color="error" onClick={() => {
              if (window.confirm('Are you sure you want to delete your account?')) deleteMutation.mutate();
            }}>
              Delete Account
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
