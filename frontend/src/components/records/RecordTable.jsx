import { Wrench, Bell } from 'lucide-react';
import { useNavigate } from "react-router-dom";

export default function RecordTable({
  records,
  field,
  onEdit,
  hasCategory,
  isViewer,
  onAlert = () => {},
  recordType,
  alerts = [],
  onView,
}) {
  const sortedRecords = records;
  const navigate = useNavigate();

  // Depura registros incompletos antes de renderizar la tabla
  const filteredRecords = sortedRecords.filter(
    r => r.id || (r.name && r.month_id && r.year_id)
  );

  // Log para ver si tienes registros incompletos
  const incomplete = sortedRecords.filter(
    r => !r.id && (!r.name || !r.month_id || !r.year_id)
  );
  if (incomplete.length) console.warn("Incomplete records:", incomplete);

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
          {filteredRecords.map((record, idx) => {
            const hasAlert = alerts.some(
              alert =>
                alert.record_id === record.id &&
                alert.record_type === recordType &&
                !alert.resolved
            );

            const fallbackKey = `${record.name || "no-name"}-${record.month_id || "no-month"}-${record.year_id || "no-year"}`;

            return (
              <tr
                key={record.id || fallbackKey || `temp-key-${idx}`}
                className="text-base"
              >
                <td className="px-4 py-2">
                  <span
                    className="text-gray-800 cursor-pointer hover:underline"
                    onClick={() => onView(record)}
                    title="Ver detalles"
                    tabIndex={0}
                    onKeyDown={e => { if (e.key === 'Enter') onView(record); }}
                    role="button"
                  >
                    {record.name}
                  </span>
                </td>
                <td className="px-4 py-2 text-green-700 font-semibold">
                  {parseFloat(record[field]).toLocaleString('es-ES', { minimumFractionDigits: 2 })} €
                </td>
                <td className="px-4 py-2 text-gray-800">{record.month_name}</td>
                <td className="px-4 py-2 text-gray-800">{record.year_value}</td>
                {hasCategory && (
                  <td className="px-4 py-2 text-gray-800">{record.category_name || record.category_id}</td>
                )}
                <td className="px-4 py-2 text-gray-800 text-right space-x-2">
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
                      onClick={() => onEdit(record)}
                      className="bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded"
                      title="Edit"
                    >
                      <Wrench size={16} />
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
