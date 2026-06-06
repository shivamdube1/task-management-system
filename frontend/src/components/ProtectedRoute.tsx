/** Route guard — redirects unauthenticated users to /login and enforces role. */

import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'admin' | 'user';
}

export default function ProtectedRoute({ children, requiredRole }: ProtectedRouteProps) {
  const { user, accessToken } = useAuthStore();

  if (!accessToken || !user) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user.role !== requiredRole) {
    // Redirect to appropriate dashboard
    const redirectPath = user.role === 'admin' ? '/admin' : '/dashboard';
    return <Navigate to={redirectPath} replace />;
  }

  return <>{children}</>;
}
