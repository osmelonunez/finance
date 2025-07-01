// components/common/Notification.jsx
export default function Notification({ type = 'success', message, onClose }) {
  if (!message) return null;

  const baseClasses = 'p-4 rounded mb-4 text-sm flex justify-between items-center shadow';
  const typeClasses = type === 'error'
    ? 'bg-red-100 text-red-800 border border-red-300'
    : 'bg-green-100 text-green-800 border border-green-300';

  return (
    <div className={`${baseClasses} ${typeClasses}`} role="alert" aria-live="assertive" aria-atomic="true">
      <span>{message}</span>
      {onClose && (
        <button
          onClick={onClose}
          aria-label="Cerrar mensaje"
          className="ml-4 font-bold text-xl leading-none hover:text-opacity-70 focus:outline-none"
        >
          &times;
        </button>
      )}
    </div>
  );
}
