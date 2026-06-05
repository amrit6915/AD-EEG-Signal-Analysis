export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
export const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:5000';

export const DETECTION_THRESHOLD_DEFAULT = 0.5;
export const SMOOTHING_WINDOW_DEFAULT = 3;
export const PEAK_HEIGHT_DEFAULT = 0.95;

export const CHANNEL_LABELS = [
  'FP1-F7', 'F7-T7', 'T7-P7', 'P7-O1',
  'FP1-F3', 'F3-C3', 'C3-P3', 'P3-O1',
  'FP2-F4', 'F4-C4', 'C4-P4', 'P4-O2',
  'FP2-F8', 'F8-T8', 'T8-P8', 'P8-O2',
  'FZ-CZ', 'CZ-PZ',
];

export const FILE_SIZE_LIMIT = 500 * 1024 * 1024;

export const TOAST_DURATION = 4000;
export const PAGINATION_LIMIT = 20;
