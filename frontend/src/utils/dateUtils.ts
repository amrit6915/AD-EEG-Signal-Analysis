import { format, formatDistanceToNow, parseISO } from 'date-fns';

export function formatRelativeTime(dateString: string): string {
  return formatDistanceToNow(parseISO(dateString), { addSuffix: true });
}

export function formatDateTime(dateString: string): string {
  return format(parseISO(dateString), 'MMM d, yyyy HH:mm');
}

export function formatDateOnly(dateString: string): string {
  return format(parseISO(dateString), 'MMM d, yyyy');
}

export function getDaysAgo(days: number): string {
  const date = new Date();
  date.setDate(date.getDate() - days);
  return date.toISOString();
}
