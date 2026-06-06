/** User Dashboard — view assigned tasks, update status. */

import { useMemo, useState } from 'react';
import {
  LayoutDashboard,
  ClipboardList,
  Clock,
  CheckCircle2,
  AlertTriangle,
  LogOut,
  Menu,
  X,
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { useAuth } from '../hooks/useAuth';
import { useTasks } from '../hooks/useTasks';
import TaskCard from '../components/TaskCard';
import toast, { Toaster } from 'react-hot-toast';

export default function UserDashboard() {
  const { user } = useAuthStore();
  const { logout } = useAuth();
  const { tasks, loading, updateStatus } = useTasks({ isAdmin: false });
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Computed stats
  const stats = useMemo(() => {
    const total = tasks.length;
    const pending = tasks.filter((t) => t.status === 'pending').length;
    const inProgress = tasks.filter((t) => t.status === 'in_progress').length;
    const completed = tasks.filter((t) => t.status === 'completed').length;
    const overdue = tasks.filter(
      (t) =>
        t.status !== 'completed' && new Date(t.due_at) < new Date()
    ).length;
    return { total, pending, inProgress, completed, overdue };
  }, [tasks]);

  const handleStatusUpdate = async (taskId: string, newStatus: string) => {
    try {
      await updateStatus(taskId, newStatus);
      toast.success(
        newStatus === 'completed'
          ? 'Task completed! 🎉'
          : 'Task started'
      );
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      toast.error(axiosErr.response?.data?.detail || 'Failed to update status');
    }
  };

  return (
    <div className="app-layout">
      <Toaster position="top-right" />

      {/* Mobile header */}
      <div className="mobile-header">
        <button className="hamburger" onClick={() => setSidebarOpen(!sidebarOpen)}>
          {sidebarOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
        <span style={{ fontWeight: 700, fontSize: 16 }}>TaskFlow</span>
        <div style={{ width: 40 }} />
      </div>

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">T</div>
          <span className="sidebar-brand-text">TaskFlow</span>
        </div>

        <nav className="sidebar-nav">
          <button className="sidebar-link active">
            <LayoutDashboard size={18} />
            My Tasks
          </button>
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="sidebar-avatar">
              {user?.name?.charAt(0).toUpperCase()}
            </div>
            <div className="sidebar-user-info">
              <div className="sidebar-user-name">{user?.name}</div>
              <div className="sidebar-user-role">{user?.role}</div>
            </div>
          </div>
          <button
            className="sidebar-link"
            onClick={logout}
            style={{ marginTop: 8, color: 'var(--accent-rose)' }}
          >
            <LogOut size={18} />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="main-content">
        <div className="page-header">
          <div>
            <h1 className="page-title">My Tasks</h1>
            <p className="page-subtitle">
              View and manage your assigned tasks
            </p>
          </div>
        </div>

        {/* Stats grid */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">
              <ClipboardList size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
              Total Assigned
            </div>
            <div className="stat-value">{stats.total}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">
              <Clock size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
              Pending
            </div>
            <div className="stat-value" style={{ background: 'linear-gradient(135deg, var(--status-pending), #f59e0b)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              {stats.pending}
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">
              <CheckCircle2 size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
              Completed
            </div>
            <div className="stat-value" style={{ background: 'linear-gradient(135deg, var(--accent-emerald), #10b981)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              {stats.completed}
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">
              <AlertTriangle size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
              Overdue
            </div>
            <div className="stat-value" style={{ background: 'linear-gradient(135deg, var(--accent-rose), #ef4444)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              {stats.overdue}
            </div>
          </div>
        </div>

        {/* Task list */}
        {loading ? (
          <div className="loading-center">
            <div className="spinner spinner-lg" />
          </div>
        ) : tasks.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">
              <ClipboardList size={28} />
            </div>
            <div className="empty-state-title">No tasks assigned</div>
            <p className="empty-state-text">
              Tasks assigned to you by an admin will appear here.
            </p>
          </div>
        ) : (
          <div className="task-grid">
            {tasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                isAdmin={false}
                onStatusUpdate={handleStatusUpdate}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
