import { useAppSelector, useAppDispatch } from '../store/hooks';
import { login, register, logout, fetchProfile } from '../store/slices/authSlice';
import type { LoginCredentials, RegisterData } from '../types';
import { useCallback } from 'react';

export function useAuth() {
  const dispatch = useAppDispatch();
  const { user, isAuthenticated, loading } = useAppSelector((state) => state.auth);

  const loginUser = useCallback(
    (credentials: LoginCredentials) => dispatch(login(credentials)).unwrap(),
    [dispatch]
  );

  const registerUser = useCallback(
    (data: RegisterData) => dispatch(register(data)).unwrap(),
    [dispatch]
  );

  const logoutUser = useCallback(() => dispatch(logout()), [dispatch]);

  const refreshProfile = useCallback(() => dispatch(fetchProfile()), [dispatch]);

  return {
    user,
    isAuthenticated,
    loading,
    loginUser,
    registerUser,
    logoutUser,
    refreshProfile,
  };
}
