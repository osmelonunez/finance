import { Copy, Wrench, Trash2 } from 'lucide-react';

export default function ExpensesTable({ expenses, onEdit, onDelete, onCopy }) {
  return (
    <div className="overflow-x-auto border rounded-lg">
      <table className="min-w-full divide-y divide-gray-200 text-lg">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-4 py-2 text-left font-semibold text-gray-700">Name</th>
            <th className="px-4 py-2 text-left font-semibold text-gray-700">Cost</th>
            <th className="px-4 py-2 text-left font-semibold text-gray-700">Category</th>
            <th className="px-4 py-2 text-left font-semibold text-gray-700">Month</th>
            <th className="px-4 py-2 text-left font-semibold text-gray-700">Year</th>
            <th className="px-4 py-2 text-right font-semibold text-gray-700">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-100 text-base">
          {expenses.map((expense) => (
            <tr key={expense.id}>
              <td className="px-4 py-2 text-gray-800">{expense.name}</td>
              <td className="px-4 py-2 text-red-700 font-semibold">
                {parseFloat(expense.cost).toLocaleString('es-ES', { minimumFractionDigits: 2 })} €
              </td>
              <td className="px-4 py-2 text-gray-800">{expense.category_name}</td>
              <td className="px-4 py-2 text-gray-800">{expense.month_name}</td>
              <td className="px-4 py-2 text-gray-800">{expense.year_value}</td>
              <td className="px-4 py-2 text-right space-x-2">
                <button
                  onClick={() => onCopy(expense)}
                  className="bg-cyan-500 hover:bg-cyan-600 text-white px-2 py-1 rounded"
                  title="Copy"
                >
                  <Copy size={16} />
                </button>
                <button
                  onClick={() => onEdit(expense)}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded"
                  title="Edit"
                >
                  <Wrench size={16} />
                </button>
                <button
                  onClick={() => onDelete(expense)}
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
