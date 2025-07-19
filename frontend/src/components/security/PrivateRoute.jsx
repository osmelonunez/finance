import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../auth/AuthContext';

export default function PrivateRoute({ children }) {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  return isAuthenticated
    ? children
    : <Navigate to="/login" state={{ from: location }} replace />;
}
