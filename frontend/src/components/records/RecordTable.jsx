import { Wrench, Trash2, Copy, Info, Bell } from 'lucide-react';
import { useNavigate } from "react-router-dom";

export default function RecordTable({
  records,
  field,
  onEdit,
  onDelete,
  onCopy,
  hasCategory,
  onInfo,
  isViewer,
  onAlert = () => {},
  recordType,
  alerts = [], // <--- NUEVO: acepta las alertas como prop
}) {
  const sortedRecords = records;
  const navigate = useNavigate();

  return (
    <div className="overflow-x-auto border rounded-lg">
      <table className="min-w-full divide-y divide-gray-200 text-lg">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-4 py-2 text-left font-semibold text-gray-700">Name</th>
            <th className="px-4 py-2 text-left font-semibold text-gray-700 capitalize">{field}</th>
            <th className="px-4 py-2 text-left font-semibold text-gray-700">Month</th>
            <th className="px-4 py-2 text-left font-semibold text-gray-700">Year</th>
            {hasCategory && (
              <th className="px-4 py-2 text-left font-semibold text-gray-700">Category</th>
            )}
            <th className="px-4 py-2 text-right font-semibold text-gray-700">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-100">
          {sortedRecords.map((record) => {
            // NUEVO: Verifica si este registro tiene alerta activa
            const hasAlert = alerts.some(
              alert =>
                alert.record_id === record.id &&
                alert.record_type === recordType &&
                !alert.resolved // Solo activas
            );

            return (
              <tr key={record.id} className="text-base">
                <td className="px-4 py-2 text-gray-800">{record.name}</td>
                <td className="px-4 py-2 text-green-700 font-semibold">
                  {parseFloat(record[field]).toLocaleString('es-ES', { minimumFractionDigits: 2 })} €
                </td>
                <td className="px-4 py-2 text-gray-800">{record.month_name}</td>
                <td className="px-4 py-2 text-gray-800">{record.year_value}</td>
                {hasCategory && (
                  <td className="px-4 py-2 text-gray-800">{record.category_name || record.category_id}</td>
                )}
                <td className="px-4 py-2 text-gray-800 text-right space-x-2">
                  <button
                    onClick={() => onInfo(record)}
                    className={
                      record.source === 'general_savings'
                        ? "bg-orange-200 hover:bg-orange-300 text-orange-700 px-2 py-1 rounded"
                        : "bg-gray-200 hover:bg-gray-300 text-gray-700 px-2 py-1 rounded"
                    }
                    title="Info"
                  >
                    <Info size={16} />
                  </button>
                  {/* === Botón ALERTA ACTUALIZADO === */}
                  {!isViewer && (
                  <button
                    onClick={() =>
                      hasAlert
                        ? navigate("/alerts")
                        : onAlert({ ...record, record_type: recordType })
                    }
                    className={
                      hasAlert
                        ? "bg-orange-200 hover:bg-orange-300 text-orange-700 px-2 py-1 rounded"
                        : "bg-gray-200 hover:bg-gray-300 text-gray-700 px-2 py-1 rounded"
                    }
                    title={hasAlert ? "See alerts" : "Add alert"}
                  >
                    <Bell size={16} />
                  </button>
                  )}
                  {!isViewer && (
                    <button
                      onClick={() => onCopy(record)}
                      className="bg-cyan-500 hover:bg-cyan-600 text-white px-2 py-1 rounded"
                      title="Copy"
                    >
                      <Copy size={16} />
                    </button>
                  )}
                  {!isViewer && (
                    <button
                      onClick={() => onEdit(record)}
                      className="bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded"
                      title="Edit"
                    >
                      <Wrench size={16} />
                    </button>
                  )}
                  {!isViewer && (
                    <button
                      onClick={() => onDelete(record)}
                      className="bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded"
                      title="Delete"
                    >
                      <Trash2 size={16} />
                    </button>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
