import api from './api';
import type { FileRecord } from '../types';

export async function uploadFile(file: File, fileType: 'edf' | 'seizures'): Promise<FileRecord> {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post(`/api/files/upload?file_type=${fileType}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function getFiles(params: {
  page?: number;
  limit?: number;
  file_type?: string;
}): Promise<{ files: FileRecord[]; total: number; page: number; limit: number; total_pages: number }> {
  const response = await api.get('/api/files/list', { params });
  return response.data;
}

export async function getFile(fileId: string): Promise<FileRecord> {
  const response = await api.get(`/api/files/${fileId}`);
  return response.data;
}

export async function downloadFile(fileId: string): Promise<Blob> {
  const response = await api.get(`/api/files/${fileId}/download`, {
    responseType: 'blob',
  });
  return response.data;
}

export async function deleteFile(fileId: string): Promise<void> {
  await api.delete(`/api/files/${fileId}`);
}
