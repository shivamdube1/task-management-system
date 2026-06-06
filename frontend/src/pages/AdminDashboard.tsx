/** Admin Dashboard — full CRUD + filters + stats. */

import { useState, useMemo, useEffect } from 'react';
import {
  LayoutDashboard,
  Plus,
  ListFilter,
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
import TaskForm from '../components/TaskForm';
import type { Task, TaskCreate, TaskUpdate, User } from '../types';
import api from '../api/axios';
import toast, { Toaster } from 'react-hot-toast';

export default function AdminDashboard() {
  const { user } = useAuthStore();
  const { logout } = useAuth();
  const { tasks, loading, createTask, updateTask, deleteTask } = useTasks({
    isAdmin: true,
  });

  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [filterStatus, setFilterStatus] = useState('');
  const [filterPriority, setFilterPriority] = useState('');
  const [filterUser, setFilterUser] = useState('');
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Fetch user list for filter dropdown
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const { data } = await api.get<User[]>('/api/users');
        setAllUsers(data);
      } catch {
        // Non-critical — filter dropdown will be empty
      }
    };
    fetchUsers();
  }, []);

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

  // Filtered tasks
  const filteredTasks = useMemo(() => {
    return tasks.filter((t) => {
      if (filterStatus && t.status !== filterStatus) return false;
      if (filterPriority && t.priority !== filterPriority) return false;
      if (filterUser && t.assigned_to !== filterUser) return false;
      return true;
    });
  }, [tasks, filterStatus, filterPriority, filterUser]);

  const handleCreate = async (data: Record<string, unknown>) => {
    await createTask(data as unknown as TaskCreate);
    toast.success('Task created successfully');
  };

  const handleUpdate = async (data: Record<string, unknown>) => {
    if (!editingTask) return;
    await updateTask(editingTask.id, data as unknown as TaskUpdate);
    toast.success('Task updated successfully');
  };

  const handleDelete = async (taskId: string) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;
    try {
      await deleteTask(taskId);
      toast.success('Task deleted');
    } catch {
      toast.error('Failed to delete task');
    }
  };

  const handleEdit = (task: Task) => {
    setEditingTask(task);
    setShowForm(true);
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingTask(null);
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
            Dashboard
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
            <h1 className="page-title">Admin Dashboard</h1>
            <p className="page-subtitle">Manage and track all tasks</p>
          </div>
          <button
            className="btn btn-primary"
            onClick={() => {
              setEditingTask(null);
              setShowForm(true);
            }}
          >
            <Plus size={16} />
            Create Task
          </button>
        </div>

        {/* Stats grid */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">
              <ClipboardList size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
              Total Tasks
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

        {/* Filter bar */}
        <div className="filter-bar">
          <ListFilter size={16} style={{ color: 'var(--text-muted)' }} />
          <select
            className="form-select"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
          <select
            className="form-select"
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
          >
            <option value="">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <select
            className="form-select"
            value={filterUser}
            onChange={(e) => setFilterUser(e.target.value)}
          >
            <option value="">All Users</option>
            {allUsers.map((u) => (
              <option key={u.id} value={u.id}>
                {u.name}
              </option>
            ))}
          </select>
          {(filterStatus || filterPriority || filterUser) && (
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => {
                setFilterStatus('');
                setFilterPriority('');
                setFilterUser('');
              }}
            >
              Clear Filters
            </button>
          )}
        </div>

        {/* Task grid */}
        {loading ? (
          <div className="loading-center">
            <div className="spinner spinner-lg" />
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">
              <ClipboardList size={28} />
            </div>
            <div className="empty-state-title">No tasks found</div>
            <p className="empty-state-text">
              {filterStatus || filterPriority
                ? 'Try adjusting your filters'
                : 'Click "Create Task" to get started'}
            </p>
          </div>
        ) : (
          <div className="task-grid">
            {filteredTasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                isAdmin
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </main>

      {/* Task form modal */}
      {showForm && (
        <TaskForm
          task={editingTask}
          onSubmit={editingTask ? handleUpdate : handleCreate}
          onClose={handleCloseForm}
        />
      )}
    </div>
  );
}
