/** Zustand auth store — manages user state, tokens, and persistence. */

import { create } from 'zustand';
import type { User } from '../types';

interface AuthStore {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  setAuth: (user: User, accessToken: string, refreshToken: string) => void;
  setAccessToken: (token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: JSON.parse(localStorage.getItem('tms_user') || 'null'),
  accessToken: localStorage.getItem('tms_access_token'),
  refreshToken: localStorage.getItem('tms_refresh_token'),

  setAuth: (user, accessToken, refreshToken) => {
    localStorage.setItem('tms_user', JSON.stringify(user));
    localStorage.setItem('tms_access_token', accessToken);
    localStorage.setItem('tms_refresh_token', refreshToken);
    set({ user, accessToken, refreshToken });
  },

  setAccessToken: (token) => {
    localStorage.setItem('tms_access_token', token);
    set({ accessToken: token });
  },

  logout: () => {
    localStorage.removeItem('tms_user');
    localStorage.removeItem('tms_access_token');
    localStorage.removeItem('tms_refresh_token');
    set({ user: null, accessToken: null, refreshToken: null });
  },
}));
