/** Shared TypeScript interfaces for the application. */

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
  is_active: boolean;
  created_at: string;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'in_progress' | 'completed';
  due_at: string;
  assigned_to: string | null;
  created_by: string;
  created_at: string;
  updated_at: string | null;
  assignee: User | null;
  creator: User | null;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: string;
  status?: string;
  due_at: string;
  assigned_to?: string | null;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: string;
  status?: string;
  due_at?: string;
  assigned_to?: string | null;
}

export interface StatusUpdate {
  status: string;
}
