/** Tasks hook — CRUD operations and polling for task data. */

import { useState, useEffect, useCallback } from 'react';
import api from '../api/axios';
import type { Task, TaskCreate, TaskUpdate } from '../types';

const POLL_INTERVAL = 30000; // 30 seconds

interface UseTasksOptions {
  isAdmin?: boolean;
  pollEnabled?: boolean;
}

export function useTasks(options: UseTasksOptions = {}) {
  const { isAdmin = false, pollEnabled = true } = options;
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      const endpoint = isAdmin ? '/api/tasks' : '/api/tasks/my';
      const { data } = await api.get<Task[]>(endpoint);
      setTasks(data);
      setError(null);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setError(axiosErr.response?.data?.detail || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }, [isAdmin]);

  useEffect(() => {
    fetchTasks();

    if (pollEnabled) {
      const interval = setInterval(fetchTasks, POLL_INTERVAL);
      return () => clearInterval(interval);
    }
  }, [fetchTasks, pollEnabled]);

  const createTask = async (taskData: TaskCreate): Promise<Task> => {
    const { data } = await api.post<Task>('/api/tasks', taskData);
    setTasks((prev) => [data, ...prev]);
    return data;
  };

  const updateTask = async (taskId: string, taskData: TaskUpdate): Promise<Task> => {
    const { data } = await api.put<Task>(`/api/tasks/${taskId}`, taskData);
    setTasks((prev) => prev.map((t) => (t.id === taskId ? data : t)));
    return data;
  };

  const deleteTask = async (taskId: string): Promise<void> => {
    await api.delete(`/api/tasks/${taskId}`);
    setTasks((prev) => prev.filter((t) => t.id !== taskId));
  };

  const updateStatus = async (taskId: string, status: string): Promise<Task> => {
    const { data } = await api.patch<Task>(`/api/tasks/${taskId}/status`, { status });
    setTasks((prev) => prev.map((t) => (t.id === taskId ? data : t)));
    return data;
  };

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    updateStatus,
  };
}
