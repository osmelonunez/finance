import { useEffect, useState } from 'react';
import jwtDecode from 'jwt-decode';
import { useNavigate } from 'react-router-dom';

export default function useTokenExpiration(token, logout) {
  const navigate = useNavigate();
  const [currentWarning, setCurrentWarning] = useState(null);

  useEffect(() => {
    if (!token) return;

    let timers = [];

    try {
      const { exp } = jwtDecode(token);
      if (!exp) return;

      const now = Date.now();
      const expMs = exp * 1000;

      const warningTimes = [
        {
          time: expMs - 2 * 60 * 1000,
          message: 'Your session will expire in 2 minutes. Please save your work and prepare to log in again.',
          duration: 5000
        },
        {
          time: expMs - 1 * 60 * 1000,
          message: 'Your session will expire in 1 minute. Please save your work and prepare to log in again.',
          duration: 25000
        },
        {
          time: expMs - 30 * 1000,
          message: 'Your session will expire in 30 seconds. Please save your work and prepare to log in again.',
          duration: 30000
        }
      ];

      warningTimes.forEach(({ time, message, duration }) => {
        const delay = time - now;
        if (delay > 0) {
          const timer = setTimeout(() => {
            setCurrentWarning({ message, duration });
          }, delay);
          timers.push(timer);
        }
      });

      const timeToLogout = expMs - now;
      if (timeToLogout > 0) {
        const logoutTimer = setTimeout(() => {
          if (logout) logout();
          else {
            localStorage.removeItem('token');
            navigate('/login');
          }
        }, timeToLogout);
        timers.push(logoutTimer);
      } else {
        if (logout) logout();
        else {
          localStorage.removeItem('token');
          navigate('/login');
        }
      }
    } catch (error) {
      console.error('Error decoding token:', error);
    }

    return () => timers.forEach(timer => clearTimeout(timer));
  }, [token, navigate, logout]);

  // Permite limpiar el warning tras mostrarlo
  const clearWarning = () => setCurrentWarning(null);

  return { currentWarning, clearWarning };
}
