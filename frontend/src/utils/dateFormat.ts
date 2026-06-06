/** Date formatting utilities. */

import { format, isPast, parseISO } from 'date-fns';

/**
 * Format an ISO date string to a human-readable format.
 * Example: "Mon, 23 Jun 2025 at 3:30 PM"
 */
export function formatDate(isoString: string): string {
  const date = parseISO(isoString);
  return format(date, "EEE, dd MMM yyyy 'at' h:mm a");
}

/**
 * Format an ISO date string to a short format.
 * Example: "Jun 23, 2025"
 */
export function formatDateShort(isoString: string): string {
  const date = parseISO(isoString);
  return format(date, 'MMM dd, yyyy');
}

/**
 * Check if a task is overdue (due_at is in the past and status is not completed).
 */
export function isOverdue(dueAt: string, status: string): boolean {
  if (status === 'completed') return false;
  return isPast(parseISO(dueAt));
}

/**
 * Format datetime-local input value to ISO string.
 */
export function toISOString(dateStr: string): string {
  return new Date(dateStr).toISOString();
}

/**
 * Format ISO string to datetime-local input value.
 */
export function toDatetimeLocal(isoString: string): string {
  const date = new Date(isoString);
  const offset = date.getTimezoneOffset();
  const local = new Date(date.getTime() - offset * 60000);
  return local.toISOString().slice(0, 16);
}
