import api from './api';
import type { DetectionResult, DetectionHistoryItem, DashboardData, TrendsData } from '../types';

export async function startDetection(edfFileId: string, seizuresFileId: string, threshold: number = 0.5) {
  const response = await api.post('/api/predictions/detect', {
    edf_file_id: edfFileId,
    seizures_file_id: seizuresFileId,
    threshold,
  });
  return response.data;
}

export async function getDetectionStatus(taskId: string) {
  const response = await api.get(`/api/predictions/${taskId}/status`);
  return response.data;
}

export async function getDetectionResults(taskId: string): Promise<DetectionResult> {
  const response = await api.get(`/api/predictions/${taskId}/results`);
  return response.data;
}

export async function rerunDetection(taskId: string, threshold: number = 0.5) {
  const response = await api.post(`/api/predictions/${taskId}/rerun`, { threshold });
  return response.data;
}

export async function getDetectionHistory(params: {
  page?: number;
  limit?: number;
  status?: string;
}): Promise<{ detections: DetectionHistoryItem[]; total: number; page: number; limit: number; total_pages: number }> {
  const response = await api.get('/api/results/history', { params });
  return response.data;
}

export async function getResultDetail(resultId: string): Promise<DetectionResult> {
  const response = await api.get(`/api/results/${resultId}`);
  return response.data;
}

export async function deleteResult(resultId: string): Promise<void> {
  await api.delete(`/api/results/${resultId}`);
}

export async function exportResult(resultId: string, format: string = 'json') {
  const response = await api.post(`/api/results/${resultId}/export`, null, {
    params: { format },
    responseType: 'blob',
  });
  return response.data;
}

export async function getDashboard(): Promise<DashboardData> {
  const response = await api.get('/api/analytics/dashboard');
  return response.data;
}

export async function getTrends(dateRange: string = '30d'): Promise<TrendsData> {
  const response = await api.get('/api/analytics/trends', { params: { date_range: dateRange } });
  return response.data;
}
