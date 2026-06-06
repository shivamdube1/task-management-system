/** Task card component — displays a task with status/priority badges and actions. */

import { Calendar, User, ArrowRight, Pencil, Trash2 } from 'lucide-react';
import type { Task } from '../types';
import { formatDate, isOverdue } from '../utils/dateFormat';
import StatusBadge from './StatusBadge';

interface TaskCardProps {
  task: Task;
  isAdmin?: boolean;
  onStatusUpdate?: (taskId: string, newStatus: string) => void;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: string) => void;
}

const NEXT_STATUS: Record<string, string | null> = {
  pending: 'in_progress',
  in_progress: 'completed',
  completed: null,
};

const STATUS_ACTION_LABEL: Record<string, string> = {
  pending: 'Start',
  in_progress: 'Complete',
};

export default function TaskCard({
  task,
  isAdmin = false,
  onStatusUpdate,
  onEdit,
  onDelete,
}: TaskCardProps) {
  const overdue = isOverdue(task.due_at, task.status);
  const nextStatus = NEXT_STATUS[task.status];

  return (
    <div className={`task-card ${overdue ? 'task-card-overdue' : ''}`}>
      <div className="task-card-header">
        <h3 className="task-card-title">{task.title}</h3>
        <div style={{ display: 'flex', gap: '6px' }}>
          <StatusBadge type="priority" value={task.priority} />
          <StatusBadge type="status" value={task.status} />
        </div>
      </div>

      {task.description && (
        <p className="task-card-description">{task.description}</p>
      )}

      <div className="task-card-meta">
        <span className={`meta-item ${overdue ? '' : ''}`} style={overdue ? { color: 'var(--accent-rose)' } : {}}>
          <Calendar size={14} />
          {formatDate(task.due_at)}
          {overdue && <span style={{ fontWeight: 600, marginLeft: 4 }}>• Overdue</span>}
        </span>

        {task.assignee && (
          <span className="meta-item">
            <User size={14} />
            {task.assignee.name}
          </span>
        )}
      </div>

      <div className="task-card-actions">
        {/* User status transition button */}
        {!isAdmin && nextStatus && onStatusUpdate && (
          <button
            className="btn btn-primary btn-sm"
            onClick={() => onStatusUpdate(task.id, nextStatus)}
          >
            <ArrowRight size={14} />
            {STATUS_ACTION_LABEL[task.status]}
          </button>
        )}

        {/* Admin edit/delete buttons */}
        {isAdmin && onEdit && (
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => onEdit(task)}
          >
            <Pencil size={14} />
            Edit
          </button>
        )}
        {isAdmin && onDelete && (
          <button
            className="btn btn-danger btn-sm"
            onClick={() => onDelete(task.id)}
          >
            <Trash2 size={14} />
            Delete
          </button>
        )}

        {task.status === 'completed' && !isAdmin && (
          <span className="meta-item" style={{ color: 'var(--accent-emerald)' }}>
            ✓ Completed
          </span>
        )}
      </div>
    </div>
  );
}
