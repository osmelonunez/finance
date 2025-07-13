import { useEffect, useRef } from 'react';
import useTokenExpiration from './hooks/useTokenExpiration';
import { showNotification } from './components/utils/showNotification';

export default function SessionManager() {
  const token = localStorage.getItem('token');
  const logout = () => {
    localStorage.removeItem('token');
    window.location.href = '/';
  };

  const { currentWarning, clearWarning } = useTokenExpiration(token, logout);
  const lastMessage = useRef(null);

  useEffect(() => {
    if (currentWarning && currentWarning.message !== lastMessage.current) {
      // Marcar notificación como de expiración de sesión
      showNotification(
        {
          type: 'warning',
          message: currentWarning.message,
          sessionExpiration: true
        },
        0 // duración 0 = persistente
      );
      lastMessage.current = currentWarning.message;
      clearWarning();
    }
  }, [currentWarning, clearWarning]);

  return null;
}
