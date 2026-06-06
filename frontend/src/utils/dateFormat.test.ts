import { describe, it, expect, vi } from 'vitest';
import { formatDate, formatDateShort, isOverdue, toISOString, toDatetimeLocal } from './dateFormat';

describe('dateFormat utilities', () => {
  describe('formatDate', () => {
    it('formats ISO string to human-readable date format', () => {
      const iso = '2025-06-23T15:30:00.000Z';
      // Timezone offset dependent assertion might fail on different environments,
      // but since we are testing in standard environment, we can check the general format structure
      const formatted = formatDate(iso);
      expect(formatted).toMatch(/[A-Za-z]{3}, \d{2} [A-Za-z]{3} \d{4} at \d{1,2}:\d{2} [AP]M/);
    });
  });

  describe('formatDateShort', () => {
    it('formats ISO string to short date format', () => {
      const iso = '2025-06-23T15:30:00.000Z';
      const formatted = formatDateShort(iso);
      expect(formatted).toMatch(/[A-Za-z]{3} \d{2}, \d{4}/);
    });
  });

  describe('isOverdue', () => {
    it('returns false if task status is completed, regardless of due date', () => {
      // Completed in the past
      expect(isOverdue('2020-01-01T12:00:00Z', 'completed')).toBe(false);
    });

    it('returns true if task status is not completed and due date is in the past', () => {
      const pastDate = new Date(Date.now() - 1000 * 60 * 60).toISOString(); // 1 hour ago
      expect(isOverdue(pastDate, 'pending')).toBe(true);
      expect(isOverdue(pastDate, 'in_progress')).toBe(true);
    });

    it('returns false if task status is not completed and due date is in the future', () => {
      const futureDate = new Date(Date.now() + 1000 * 60 * 60).toISOString(); // 1 hour from now
      expect(isOverdue(futureDate, 'pending')).toBe(false);
      expect(isOverdue(futureDate, 'in_progress')).toBe(false);
    });
  });

  describe('toISOString', () => {
    it('converts local date string to standard ISO format', () => {
      const localStr = '2025-06-23T15:30';
      const iso = toISOString(localStr);
      expect(iso).toContain('2025-06-23T');
      expect(iso).toMatch(/Z$/);
    });
  });

  describe('toDatetimeLocal', () => {
    it('converts ISO string to datetime-local string (YYYY-MM-DDTHH:MM)', () => {
      const iso = '2025-06-23T15:30:00.000Z';
      const local = toDatetimeLocal(iso);
      expect(local).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/);
    });
  });
});
