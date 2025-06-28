import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

export default function SettingsPage() {
  const [years, setYears] = useState([]);
  const [newYear, setNewYear] = useState('');
  const [showYearModal, setShowYearModal] = useState(false);
  const [action, setAction] = useState('add');
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    fetch('/api/years')
      .then(res => res.json())
      .then(setYears);
  }, []);

  const handleYearAction = async () => {
    setErrorMessage('');
    setSuccessMessage('');
    if (!newYear.trim()) return;

    if (action === 'add') {
      if (years.some(y => y.value === parseInt(newYear))) {
        setErrorMessage('That year already exists.');
        return;
      }
      const res = await fetch('/api/years', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value: newYear.trim() })
      });
      if (res.ok) {
        const updated = await res.json();
        setYears(updated);
        setSuccessMessage('Year added successfully.');
      }
    } else if (action === 'delete') {
      const idToDelete = years.find(y => y.id === parseInt(newYear))?.id;
      if (!idToDelete) return;
      const res = await fetch(`/api/years/${idToDelete}`, { method: 'DELETE' });
      if (res.ok) {
        const updated = await res.json();
        setYears(updated);
        setSuccessMessage('Year deleted successfully.');
      } else {
        const data = await res.json();
        setErrorMessage(data.error || 'Unable to delete year.');
        return;
      }
    }

    setNewYear('');
    setShowYearModal(false);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Settings</h2>
      <p className="text-gray-600 mb-6">Manage your application preferences and configuration options.</p>

      <div className="bg-white rounded-lg shadow p-6 space-y-4">
        <h3 className="text-lg font-semibold text-gray-700">Account Settings</h3>
        <p className="text-sm text-gray-500">More options coming soon.</p>

        <div className="pt-4 space-y-2">
          <h3 className="text-md font-semibold text-gray-700">Categories</h3>
          <Link
            to="/categories"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            Manage Categories
          </Link>
        </div>

        <div className="pt-6 space-y-4">
          <h3 className="text-md font-semibold text-gray-700">Year Management</h3>

          <div className="flex gap-2">
            <button
              onClick={() => { setAction('add'); setShowYearModal(true); setErrorMessage(''); setSuccessMessage(''); }}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Add Year
            </button>
            <button
              onClick={() => { setAction('delete'); setShowYearModal(true); setErrorMessage(''); setSuccessMessage(''); }}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Delete Year
            </button>
          </div>
          {successMessage && <p className="text-sm text-green-600">{successMessage}</p>}
        </div>
      </div>

      {showYearModal && (
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
              />
            ) : (
              <select
                value={newYear}
                onChange={e => setNewYear(e.target.value)}
                className="border rounded px-3 py-2 w-full"
              >
                <option value="">Select year to delete</option>
                {years.map(y => (
                  <option key={y.id} value={y.id}>{y.value}</option>
                ))}
              </select>
            )}

            {errorMessage && <p className="text-sm text-red-600">{errorMessage}</p>}

            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowYearModal(false)}
                className="px-4 py-2 border rounded text-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={handleYearAction}
                className={`px-4 py-2 text-white rounded ${action === 'add' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'}`}
              >
                {action === 'add' ? 'Add' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}