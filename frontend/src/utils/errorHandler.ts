import axios from 'axios';

export interface ApiError {
  message: string;
  status?: number;
  details?: string;
}

export function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data;
    if (typeof data === 'string') return data;
    if (data?.detail) return data.detail;
    if (data?.message) return data.message;
    return error.message || 'An unexpected error occurred';
  }
  if (error instanceof Error) return error.message;
  return 'An unexpected error occurred';
}

export function getErrorStatus(error: unknown): number | undefined {
  if (axios.isAxiosError(error)) {
    return error.response?.status;
  }
  return undefined;
}
