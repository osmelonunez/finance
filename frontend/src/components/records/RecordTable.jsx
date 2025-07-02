import { Wrench, Trash2, Copy } from 'lucide-react';

export default function RecordTable({ records, field, onEdit, onDelete, onCopy }) {
  const sortedRecords = [...records].sort((a, b) => {
    const yearDiff = parseInt(a.year_value) - parseInt(b.year_value);
    if (yearDiff !== 0) return yearDiff;

    const monthDiff = parseInt(a.month_id) - parseInt(b.month_id);
    if (monthDiff !== 0) return monthDiff;

    return a.name.localeCompare(b.name);
  });

  return (
    <div className="overflow-x-auto border rounded-lg">
      <table className="min-w-full divide-y divide-gray-200 text-lg">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-4 py-2 text-left font-semibold text-gray-700">Name</th>
            <th className="px-4 py-2 text-left font-semibold text-gray-700 capitalize">{field}</th>
            <th className="px-4 py-2 text-left font-semibold text-gray-700">Month</th>
            <th className="px-4 py-2 text-left font-semibold text-gray-700">Year</th>
            <th className="px-4 py-2 text-right font-semibold text-gray-700">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-100">
          {sortedRecords.map((record) => (
            <tr key={record.id} className="text-base">
              <td className="px-4 py-2 text-gray-800">{record.name}</td>
              <td className="px-4 py-2 text-gray-800">{record[field]}</td>
              <td className="px-4 py-2 text-gray-800">{record.month_name}</td>
              <td className="px-4 py-2 text-gray-800">{record.year_value}</td>
              <td className="px-4 py-2 text-gray-800 text-right space-x-2">
                <button
                  onClick={() => onCopy(record)}
                  className="bg-cyan-500 hover:bg-cyan-600 text-white px-2 py-1 rounded"
                  title="Copy"
                >
                  <Copy size={16} />
                </button>
                <button
                  onClick={() => onEdit(record)}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded"
                  title="Edit"
                >
                  <Wrench size={16} />
                </button>
                <button
                  onClick={() => onDelete(record)}
                  className="bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded"
                  title="Delete"
                >
                  <Trash2 size={16} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
