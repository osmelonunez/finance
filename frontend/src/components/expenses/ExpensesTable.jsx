import { Trash2, Wrench, CopyPlus } from 'lucide-react';

export default function ExpensesTable({ expenses, onEdit, onDelete, onCopy }) {
  return (
    <table className="min-w-full bg-white shadow rounded-xl">
      <thead className="bg-gray-50 text-left">
        <tr>
          <th className="p-3">Name</th>
          <th className="p-3">Cost</th>
          <th className="p-3">Month</th>
          <th className="p-3">Year</th>
          <th className="p-3">Category</th>
          <th className="p-3">Actions</th>
        </tr>
      </thead>
      <tbody>
        {expenses.map((e, i) => (
          <tr key={i} className="border-t hover:bg-gray-50">
            <td className="p-3">{e.name}</td>
            <td className="p-3 text-red-500 font-medium">
              {parseFloat(e.cost).toLocaleString('es-ES', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })} €
            </td>
            <td className="p-3">{e.month_name}</td>
            <td className="p-3">{e.year_value}</td>
            <td className="p-3">{e.category_name}</td>
            <td className="p-3">
              <div className="inline-flex gap-1">
                <button
                  className="p-2 bg-cyan-500 text-white rounded hover:bg-cyan-600"
                  onClick={() => onCopy(e)}
                  title="Copy"
                >
                  <CopyPlus size={16} />
                </button>
                <button
                  className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  onClick={() => onEdit(e)}
                  title="Edit"
                >
                  <Wrench size={16} />
                </button>
                <button
                  className="p-2 bg-red-500 text-white rounded hover:bg-red-600"
                  onClick={() => onDelete(e)}
                  title="Delete"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
