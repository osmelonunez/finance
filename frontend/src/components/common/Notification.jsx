import React from "react";

export default function Notification(props) {
  // Validación máxima: nunca da error aunque lo llamen mal
  if (!props || typeof props !== 'object') {
    //console.log('Notification llamado con props:', props);
    return null;
  }

  const {
    type = "success",
    message,
    onClose
  } = props;

  if (!message) return null;

  const typeClasses = {
    success: "bg-green-100 text-green-800 border-green-300",
    error: "bg-red-100 text-red-800 border-red-300",
    info: "bg-blue-100 text-blue-800 border-blue-300",
    warning: "bg-yellow-100 text-yellow-800 border-yellow-300"
  };

  return (
    <div
      className={`fixed top-6 left-1/2 transform -translate-x-1/2 z-50 px-6 py-3 rounded-lg shadow-lg border ${typeClasses[type] || typeClasses.success}`}
      style={{ minWidth: 300, maxWidth: 500 }}
    >
      <div className="flex justify-between items-center">
        <span>{message}</span>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-4 text-lg font-bold focus:outline-none"
            title="Cerrar notificación"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}
