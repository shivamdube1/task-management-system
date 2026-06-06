/** Task creation/edit form with calendar date picker + time picker (not plain HTML input). */

import { useState, useEffect } from 'react';
import { DayPicker } from 'react-day-picker';
import 'react-day-picker/style.css';
import type { Task, User } from '../types';
import api from '../api/axios';
import { X, Calendar, Clock } from 'lucide-react';

interface TaskFormProps {
  task?: Task | null;
  onSubmit: (data: Record<string, unknown>) => Promise<void>;
  onClose: () => void;
}

function parseDateFromTask(task: Task | null | undefined): Date | undefined {
  if (!task?.due_at) return undefined;
  return new Date(task.due_at);
}

function parseHourFromTask(task: Task | null | undefined): string {
  if (!task?.due_at) return '12';
  return String(new Date(task.due_at).getHours()).padStart(2, '0');
}

function parseMinuteFromTask(task: Task | null | undefined): string {
  if (!task?.due_at) return '00';
  return String(new Date(task.due_at).getMinutes()).padStart(2, '0');
}

export default function TaskForm({ task, onSubmit, onClose }: TaskFormProps) {
  const [title, setTitle] = useState(task?.title || '');
  const [description, setDescription] = useState(task?.description || '');
  const [priority, setPriority] = useState(task?.priority || 'medium');
  const [status, setStatus] = useState(task?.status || 'pending');
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(parseDateFromTask(task));
  const [hour, setHour] = useState(parseHourFromTask(task));
  const [minute, setMinute] = useState(parseMinuteFromTask(task));
  const [assignedTo, setAssignedTo] = useState(task?.assigned_to || '');
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showCalendar, setShowCalendar] = useState(false);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const { data } = await api.get<User[]>('/api/users');
        setUsers(data);
      } catch {
        // If user list fails, just show an empty dropdown
      }
    };
    fetchUsers();
  }, []);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!title.trim()) newErrors.title = 'Title is required';
    if (title.length > 100) newErrors.title = 'Title must be 100 characters or less';
    if (description.length > 500)
      newErrors.description = 'Description must be 500 characters or less';
    if (!selectedDate) newErrors.date = 'Due date is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const buildISODate = (): string => {
    if (!selectedDate) return '';
    const d = new Date(selectedDate);
    d.setHours(parseInt(hour, 10), parseInt(minute, 10), 0, 0);
    return d.toISOString();
  };

  const formatDisplayDate = (): string => {
    if (!selectedDate) return 'Select date';
    const opts: Intl.DateTimeFormatOptions = {
      weekday: 'short',
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    };
    return selectedDate.toLocaleDateString('en-US', opts);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        status,
        due_at: buildISODate(),
        assigned_to: assignedTo || null,
      });
      onClose();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setErrors({ submit: axiosErr.response?.data?.detail || 'Failed to save task' });
    } finally {
      setLoading(false);
    }
  };

  // Generate hour options (0–23)
  const hours = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, '0'));
  // Generate minute options (0, 5, 10, ... 55)
  const minutes = Array.from({ length: 12 }, (_, i) => String(i * 5).padStart(2, '0'));

  // Disable past dates
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">{task ? 'Edit Task' : 'Create Task'}</h2>
          <button className="modal-close" onClick={onClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="task-title">
              Title *
            </label>
            <input
              id="task-title"
              className="form-input"
              type="text"
              placeholder="Enter task title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              maxLength={100}
            />
            {errors.title && <p className="form-error">{errors.title}</p>}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="task-description">
              Description
            </label>
            <textarea
              id="task-description"
              className="form-input"
              placeholder="Enter description (optional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              maxLength={500}
              rows={3}
              style={{ resize: 'vertical' }}
            />
            {errors.description && (
              <p className="form-error">{errors.description}</p>
            )}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="task-priority">
                Priority
              </label>
              <select
                id="task-priority"
                className="form-select"
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="task-status">
                Status
              </label>
              <select
                id="task-status"
                className="form-select"
                value={status}
                onChange={(e) => setStatus(e.target.value)}
              >
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>

          {/* Calendar Date Picker */}
          <div className="form-group">
            <label className="form-label">Due Date *</label>
            <button
              type="button"
              className="form-input"
              onClick={() => setShowCalendar(!showCalendar)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                cursor: 'pointer',
                textAlign: 'left',
                color: selectedDate ? 'var(--text-primary)' : 'var(--text-muted)',
              }}
            >
              <Calendar size={16} />
              {formatDisplayDate()}
            </button>
            {showCalendar && (
              <div className="calendar-dropdown">
                <DayPicker
                  mode="single"
                  selected={selectedDate}
                  onSelect={(date) => {
                    setSelectedDate(date);
                    setShowCalendar(false);
                  }}
                  disabled={{ before: today }}
                  classNames={{
                    root: 'rdp-dark',
                  }}
                />
              </div>
            )}
            {errors.date && <p className="form-error">{errors.date}</p>}
          </div>

          {/* Time Picker */}
          <div className="form-group">
            <label className="form-label">Due Time *</label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Clock size={16} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
              <select
                className="form-select"
                value={hour}
                onChange={(e) => setHour(e.target.value)}
                style={{ width: 'auto', minWidth: '80px' }}
                aria-label="Hour"
              >
                {hours.map((h) => (
                  <option key={h} value={h}>
                    {parseInt(h, 10) === 0
                      ? '12 AM'
                      : parseInt(h, 10) < 12
                      ? `${parseInt(h, 10)} AM`
                      : parseInt(h, 10) === 12
                      ? '12 PM'
                      : `${parseInt(h, 10) - 12} PM`}
                  </option>
                ))}
              </select>
              <span style={{ color: 'var(--text-muted)', fontWeight: 700 }}>:</span>
              <select
                className="form-select"
                value={minute}
                onChange={(e) => setMinute(e.target.value)}
                style={{ width: 'auto', minWidth: '80px' }}
                aria-label="Minute"
              >
                {minutes.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="task-assignee">
              Assign To
            </label>
            <select
              id="task-assignee"
              className="form-select"
              value={assignedTo}
              onChange={(e) => setAssignedTo(e.target.value)}
            >
              <option value="">Unassigned</option>
              {users.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.name} ({u.email})
                </option>
              ))}
            </select>
          </div>

          {errors.submit && (
            <p className="form-error" style={{ marginBottom: 16 }}>
              {errors.submit}
            </p>
          )}

          <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
            >
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading && <span className="spinner" />}
              {task ? 'Update Task' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
