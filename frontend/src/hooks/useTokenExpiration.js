import { useEffect, useState } from 'react';
import jwtDecode from 'jwt-decode';
import { useNavigate } from 'react-router-dom';

export default function useTokenExpiration(token, logout) {
  const navigate = useNavigate();
  const [warnings, setWarnings] = useState([]);

  useEffect(() => {
    if (!token) return;

    let timers = [];

    try {
      const { exp } = jwtDecode(token);
      if (!exp) return;

      const now = Date.now();
      const expMs = exp * 1000;

      const warningTimes = [
        { time: expMs - 2 * 60 * 1000, message: 'Tu sesión expirará en 2 minutos. Guarda tu trabajo.' },
        { time: expMs - 1 * 60 * 1000, message: 'Tu sesión expirará en 1 minuto. Guarda tu trabajo.' },
        { time: expMs - 30 * 1000, message: 'Tu sesión expirará en 30 segundos. Guarda tu trabajo.' }
      ];

      warningTimes.forEach(({ time, message }) => {
        const delay = time - now;
        if (delay > 0) {
          const timer = setTimeout(() => {
            setWarnings(prev => [...prev, message]);
          }, delay);
          timers.push(timer);
        } else {
          setWarnings(prev => [...prev, message]);
        }
      });

      const timeToLogout = expMs - now;
      if (timeToLogout > 0) {
        const logoutTimer = setTimeout(() => {
          if (logout) logout();
          else {
            localStorage.removeItem('token');
            navigate('/');
          }
        }, timeToLogout);
        timers.push(logoutTimer);
      } else {
        if (logout) logout();
        else {
          localStorage.removeItem('token');
          navigate('/');
        }
      }
    } catch (error) {
      console.error('Error al decodificar token:', error);
    }

    return () => timers.forEach(timer => clearTimeout(timer));
  }, [token, navigate, logout]);

  const removeWarning = (message) => {
    setWarnings(prev => prev.filter(m => m !== message));
  };

  return { warnings, removeWarning };
}
