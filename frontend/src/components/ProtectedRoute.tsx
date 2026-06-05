import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAppSelector } from '../store/hooks';
import Loading from './Loading';

interface Props {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: Props) {
  const { isAuthenticated, loading } = useAppSelector((state) => state.auth);

  if (loading) return <Loading />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  return <>{children}</>;
}
