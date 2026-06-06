/** Auth hook — login, register, and session management. */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { useAuthStore } from '../store/authStore';
import type { User, TokenResponse } from '../types';

export function useAuth() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { setAuth, logout: storeLogout } = useAuthStore();
  const navigate = useNavigate();

  const login = async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const { data: tokens } = await api.post<TokenResponse>('/api/auth/login', {
        email,
        password,
      });

      // Fetch user profile
      const { data: user } = await api.get<User>('/api/auth/me', {
        headers: { Authorization: `Bearer ${tokens.access_token}` },
      });

      setAuth(user, tokens.access_token, tokens.refresh_token);

      // Redirect based on role
      if (user.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setError(axiosErr.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const register = async (
    name: string,
    email: string,
    password: string,
    role: string = 'user'
  ) => {
    setLoading(true);
    setError(null);
    try {
      await api.post('/api/auth/register', { name, email, password, role });
      // Auto-login after registration
      await login(email, password);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setError(axiosErr.response?.data?.detail || 'Registration failed');
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await api.post('/api/auth/logout');
    } catch {
      // Ignore — stateless logout
    }
    storeLogout();
    navigate('/login');
  };

  return { login, register, logout, loading, error, setError };
}
