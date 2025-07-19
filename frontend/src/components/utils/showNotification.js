// showNotification.js

let showNotification = ({ type, message }, duration = 2000) => {
  if (!type && !message) return; // ignora llamadas vacías
  throw new Error(
    'showNotification no está inicializado. Asegúrate de envolver tu app en <NotificationProvider />'
  );
};

export const setShowNotification = (fn) => {
  showNotification = (notification, duration = 2000) => {
    if (!notification || typeof notification !== 'object') return;
    if (!notification.message) return;
    fn(notification, duration);
  };
};

export { showNotification };
