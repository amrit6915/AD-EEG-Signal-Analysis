export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function formatProbability(prob: number): string {
  return (prob * 100).toFixed(1) + '%';
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatShortDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
}

export function truncateFilename(name: string, maxLen: number = 30): string {
  if (name.length <= maxLen) return name;
  const ext = name.split('.').pop();
  const nameWithoutExt = name.slice(0, name.lastIndexOf('.'));
  return nameWithoutExt.slice(0, maxLen - 3 - (ext?.length || 0)) + '...' + (ext ? '.' + ext : '');
}
