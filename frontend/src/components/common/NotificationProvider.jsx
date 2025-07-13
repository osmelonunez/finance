import React, { useState, useEffect } from "react";
import Notification from "./Notification";
import { setShowNotification } from "../utils/showNotification"; // Ajusta el path si es necesario

export const NotificationProvider = ({ children }) => {
  const [notification, setNotification] = useState(null);
  const [timeoutId, setTimeoutId] = useState(null);

  useEffect(() => {
    setShowNotification((incomingNotification, duration = 2000) => {
      // Si ya hay una notificación de expiración visible,
      // solo permite otra de expiración (bloquea el resto)
      if (notification && notification.sessionExpiration) {
        if (!incomingNotification.sessionExpiration) {
          return; // Ignora las notificaciones normales
        }
      }

      setNotification(incomingNotification);

      // Limpiar timeout anterior
      if (timeoutId) clearTimeout(timeoutId);

      // Si es de expiración de sesión, no se autodescarta
      if (incomingNotification.sessionExpiration) {
        return;
      }

      // Notificaciones normales: autodescartar
      if (duration > 0) {
        const id = setTimeout(() => {
          setNotification(null);
        }, duration);
        setTimeoutId(id);
      }
    });

    // Limpiar al desmontar
    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
    // eslint-disable-next-line
  }, [notification, timeoutId]);

  return (
    <>
      {notification && (
        <Notification
          type={notification.type}
          message={notification.message}
          onClose={() => setNotification(null)}
        />
      )}
      {children}
    </>
  );
};
