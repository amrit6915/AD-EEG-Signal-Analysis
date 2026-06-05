import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import type { User, AuthState, LoginCredentials, RegisterData } from '../../types';
import * as authService from '../../services/authService';

const initialState: AuthState = {
  user: null,
  accessToken: localStorage.getItem('access_token'),
  refreshToken: localStorage.getItem('refresh_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  loading: false,
};

export const login = createAsyncThunk('auth/login', async (credentials: LoginCredentials) => {
  const response = await authService.loginUser(credentials);
  localStorage.setItem('access_token', response.access_token);
  localStorage.setItem('refresh_token', response.refresh_token);
  const user = await authService.getProfile();
  return { user, ...response };
});

export const register = createAsyncThunk('auth/register', async (data: RegisterData) => {
  const response = await authService.registerUser(data);
  localStorage.setItem('access_token', response.access_token);
  localStorage.setItem('refresh_token', response.refresh_token);
  const user = await authService.getProfile();
  return { user, ...response };
});

export const fetchProfile = createAsyncThunk('auth/fetchProfile', async () => {
  const user = await authService.getProfile();
  return user;
});

export const logout = createAsyncThunk('auth/logout', async () => {
  try {
    await authService.logoutUser();
  } catch {
    // ignore
  } finally {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setUser(state, action: PayloadAction<User>) {
      state.user = action.payload;
    },
    clearAuth(state) {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => { state.loading = true; })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.accessToken = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
      })
      .addCase(login.rejected, (state) => {
        state.loading = false;
        state.isAuthenticated = false;
      })
      .addCase(register.pending, (state) => { state.loading = true; })
      .addCase(register.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.accessToken = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
      })
      .addCase(register.rejected, (state) => {
        state.loading = false;
        state.isAuthenticated = false;
      })
      .addCase(fetchProfile.fulfilled, (state, action) => {
        state.user = action.payload;
      })
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.accessToken = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
      });
  },
});

export const { setUser, clearAuth } = authSlice.actions;
export default authSlice.reducer;
