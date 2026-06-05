export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  loading: boolean;
}

export interface FileRecord {
  id: string;
  original_filename: string;
  file_type: 'edf' | 'seizures';
  file_size: number;
  uploaded_at: string;
  metadata?: Record<string, unknown>;
}

export interface DetectionSummary {
  seizure_detected: boolean;
  max_probability: number;
  num_peaks: number;
  threshold_used: number;
  total_windows: number;
}

export interface DetectionResult {
  id: string;
  detection_id: string;
  raw_predictions: number[];
  smoothed_predictions: number[];
  detected_peaks: Peak[];
  summary: DetectionSummary;
  visualization_data?: string;
  created_at: string;
}

export interface Peak {
  timestamp: number;
  probability: number;
  index: number;
}

export interface DetectionHistoryItem {
  id: string;
  edf_filename?: string;
  seizures_filename?: string;
  status: string;
  started_at: string;
  completed_at?: string;
  seizure_detected?: boolean;
  max_probability?: number;
  threshold_used: number;
}

export interface DashboardData {
  total_detections: number;
  seizures_detected: number;
  detection_rate: number;
  avg_probability: number;
  total_files: number;
  recent_detections: DetectionHistoryItem[];
}

export interface TrendsData {
  dates: string[];
  detection_counts: number[];
  seizure_counts: number[];
  avg_probabilities: number[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}
