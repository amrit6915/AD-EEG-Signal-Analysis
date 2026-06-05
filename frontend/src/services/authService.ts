import api from './api';
import type { LoginCredentials, RegisterData, TokenResponse, User } from '../types';

export async function loginUser(data: LoginCredentials): Promise<TokenResponse> {
  const response = await api.post('/api/auth/login', data);
  return response.data;
}

export async function registerUser(data: RegisterData): Promise<TokenResponse> {
  const response = await api.post('/api/auth/register', data);
  return response.data;
}

export async function refreshToken(refresh_token: string): Promise<TokenResponse> {
  const response = await api.post('/api/auth/refresh', { refresh_token });
  return response.data;
}

export async function logoutUser(): Promise<void> {
  await api.post('/api/auth/logout');
}

export async function getProfile(): Promise<User> {
  const response = await api.get('/api/users/profile');
  return response.data;
}

export async function updateProfile(data: Partial<User>): Promise<User> {
  const response = await api.put('/api/users/profile', data);
  return response.data;
}

export async function getLoginHistory() {
  const response = await api.get('/api/users/login-history');
  return response.data;
}

export async function changePassword(currentPassword: string, newPassword: string) {
  const response = await api.post('/api/users/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
  });
  return response.data;
}

export async function deleteAccount() {
  await api.delete('/api/users/account');
}
