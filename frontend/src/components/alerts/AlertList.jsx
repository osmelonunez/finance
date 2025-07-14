import React from "react";
import { Wrench, Trash2, CheckCircle } from "lucide-react";

export default function AlertList({ alerts, onResolve, onEdit, onDelete, editAlert }) {
  // Filtrar según lo pedido
  const filteredAlerts = alerts.filter(alert => {
    if (!alert.resolved) return true;
    if (!alert.resolved_at) return false;
    const resolvedAt = new Date(alert.resolved_at);
    const now = new Date();
    const diffHours = (now - resolvedAt) / (1000 * 60 * 60);
    return diffHours <= 24;
  });

  return (
    <ul>
      {filteredAlerts.map(alert => (
        <li
          key={alert.id}
          className={`mb-2 px-4 py-2 rounded border bg-white flex flex-col md:flex-row justify-between items-start md:items-center
            ${alert.resolved ? "border-gray-300 shadow-none text-gray-400" : "border-gray-200 shadow-[0_2px_8px_rgba(253,224,71,0.2)] text-black"}
          `}
        >
          <div className="flex-1">
            <span className="font-medium">{alert.message}</span>
            <span className="block text-xs text-gray-400 mt-1">
              {alert.created_at && <span>Created: {alert.created_at.slice(0,10)} | </span>}
              {alert.created_by_name && <span>By: {alert.created_by_name}</span>}
              {alert.due_date && <span> | Target date: {alert.due_date.slice(0,10)}</span>}
            </span>
            {/* 👇 Aquí va la línea adicional, sin fondo, solo como texto */}
            {alert.record_type && alert.record_name && (
              <span className="block text-xs text-gray-500 mt-1">
                <b>{alert.record_type[0].toUpperCase() + alert.record_type.slice(1)}</b>
                {": "}
                {alert.record_name}
              </span>
            )}
            {alert.resolved && (
              <span className="block text-xs text-green-600 mt-1">
                Resolved
                {alert.resolved_by_name && ` by ${alert.resolved_by_name}`}
                {alert.resolved_at && ` on ${alert.resolved_at.slice(0,10)}`}
              </span>
            )}
          </div>
          {!alert.resolved && (
            <div className="flex gap-2 mt-2 md:mt-0">
              <button
                onClick={() => onResolve(alert.id)}
                className="bg-green-500 text-white text-xs p-2 rounded hover:bg-green-600 flex items-center"
                title="Mark as resolved"
              >
                <CheckCircle size={16} />
              </button>
              <button
                onClick={() => onEdit(alert)}
                className={
                  `text-xs p-2 rounded flex items-center
                  ${editAlert && editAlert.id === alert.id 
                    ? "bg-yellow-100 text-yellow-600 border border-yellow-500" // Color modo edición
                    : "bg-blue-500 text-white hover:bg-blue-600"}`
                }
                title="Edit alert"
              >
                <Wrench size={16} />
              </button>
            </div>
          )}
        </li>
      ))}
    </ul>
  );
}
