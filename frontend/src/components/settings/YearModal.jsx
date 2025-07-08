export default function YearModal({
  isOpen,
  onClose,
  action,
  newYear,
  setNewYear,
  years = [],
  errorMessage,
  successMessage,
  onSubmit,
  loading = false
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded-xl w-full max-w-sm shadow-lg space-y-4">
        <h3 className="text-lg font-semibold text-gray-800">
          {action === 'add' ? 'Add New Year' : 'Delete Year'}
        </h3>
        {action === 'add' ? (
          <input
            type="number"
            value={newYear}
            onChange={e => setNewYear(e.target.value)}
            placeholder="Enter year"
            className="border rounded px-3 py-2 w-full"
            disabled={loading}
          />
        ) : (
          <select
            value={newYear}
            onChange={e => setNewYear(e.target.value)}
            className="border rounded px-3 py-2 w-full"
            disabled={loading}
          >
            <option value="">Select year to delete</option>
            {years.map(y => (
              <option key={y.id} value={y.id}>{y.value}</option>
            ))}
          </select>
        )}

        {errorMessage && <p className="text-sm text-red-600">{errorMessage}</p>}
        {successMessage && <p className="text-sm text-green-600">{successMessage}</p>}

        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 border rounded text-gray-600"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            onClick={onSubmit}
            className={`px-4 py-2 text-white rounded ${action === 'add' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'}`}
            disabled={loading}
          >
            {loading
              ? (action === 'add' ? 'Adding...' : 'Deleting...')
              : (action === 'add' ? 'Add' : 'Delete')}
          </button>
        </div>
      </div>
    </div>
  );
}
