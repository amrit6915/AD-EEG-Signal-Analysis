import React, { useEffect, useMemo } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { useAppSelector } from './store/hooks';
import { useAuth } from './hooks/useAuth';
import { lightTheme, darkTheme } from './styles/theme';

import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import ProtectedRoute from './components/ProtectedRoute';
import ToastContainer from './components/common/Toast';

import LoginPage from './pages/Login';
import RegisterPage from './pages/Register';
import DashboardPage from './pages/Dashboard';
import DetectionPage from './pages/Detection';
import ResultsPage from './pages/Results';
import FileManagementPage from './pages/FileManagement';
import ProfilePage from './pages/Profile';
import AnalyticsPage from './pages/Analytics';
import NotFoundPage from './pages/NotFound';

function AppLayout({ children }: { children: React.ReactNode }) {
  const sidebarOpen = useAppSelector((state) => state.ui.sidebarOpen);
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Navbar />
      <Sidebar />
      <main
        style={{
          flexGrow: 1,
          marginTop: 64,
          marginLeft: sidebarOpen ? 240 : 0,
          padding: 24,
          transition: 'margin-left 0.3s ease',
          backgroundColor: '#F5F5F5',
          minHeight: 'calc(100vh - 64px)',
        }}
      >
        {children}
      </main>
    </div>
  );
}

function App() {
  const darkMode = useAppSelector((state) => state.ui.darkMode);
  const theme = useMemo(() => (darkMode ? darkTheme : lightTheme), [darkMode]);
  const { isAuthenticated, refreshProfile } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      refreshProfile();
    }
  }, [isAuthenticated, refreshProfile]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ToastContainer />
      <Routes>
        <Route path="/login" element={!isAuthenticated ? <LoginPage /> : <Navigate to="/dashboard" />} />
        <Route path="/register" element={!isAuthenticated ? <RegisterPage /> : <Navigate to="/dashboard" />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <AppLayout>
                <DashboardPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/detection"
          element={
            <ProtectedRoute>
              <AppLayout>
                <DetectionPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/results"
          element={
            <ProtectedRoute>
              <AppLayout>
                <ResultsPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/results/:id"
          element={
            <ProtectedRoute>
              <AppLayout>
                <ResultsPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/files"
          element={
            <ProtectedRoute>
              <AppLayout>
                <FileManagementPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <AppLayout>
                <ProfilePage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <AppLayout>
                <AnalyticsPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />

        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </ThemeProvider>
  );
}

export default App;
