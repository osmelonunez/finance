export function showNotification(setNotification, notification, duration = 2000) {
  setNotification(notification);
  setTimeout(() => setNotification(null), duration);
}
