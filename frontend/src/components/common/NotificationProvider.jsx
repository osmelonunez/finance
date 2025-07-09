import React, { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react';
import Notification from './Notification';
import { setShowNotification } from '../utils/showNotification';

const NotificationContext = createContext();

export function useNotification() {
  return useContext(NotificationContext);
}

export function NotificationProvider({ children }) {
  const [notification, setNotification] = useState(null);
  const timerRef = useRef(null);

  const showNotification = useCallback(({ type, message }, duration = 2000) => {
    setNotification({ type, message });
    // Limpia cualquier timeout anterior
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => setNotification(null), duration);
  }, []);

  useEffect(() => {
    setShowNotification(showNotification);
    // Limpia el timeout si el componente se desmonta
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [showNotification]);

  const closeNotification = () => {
    setNotification(null);
    if (timerRef.current) clearTimeout(timerRef.current);
  };

  return (
    <NotificationContext.Provider value={{ showNotification }}>
      {children}
      {notification && (
        <Notification
          type={notification.type}
          message={notification.message}
          onClose={closeNotification}
        />
      )}
    </NotificationContext.Provider>
  );
}
