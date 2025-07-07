import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Layers, Calendar, Settings, Users, Plus, Trash, Database, Edit, FolderPlus, CalendarPlus, CalendarMinus, User } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';

export default function SettingsPage() {
  const [years, setYears] = useState([]);
  const [newYear, setNewYear] = useState('');
  const [showYearModal, setShowYearModal] = useState(false);
  const [action, setAction] = useState('add');
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const { user } = useAuth();
  const showManageUsers = user?.role === 'admin';
  const [showSchedule, setShowSchedule] = useState(false);
  const [scheduleDays, setScheduleDays] = useState([]);
  const [scheduleTime, setScheduleTime] = useState('');

  useEffect(() => {
    fetch('/api/years', {
  headers: {
    Authorization: `Bearer ${localStorage.getItem('token')}`
  }
})
      .then(res => res.json())
      .then(setYears);
  }, []);

  useEffect(() => {
    if (showSchedule) {
      fetch('/api/backup/schedule')
        .then(res => res.json())
        .then(data => {
          setScheduleDays(data.days || []);
          setScheduleTime(data.time || '');
        });
    }
  }, [showSchedule]);

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

      <div className="bg-white rounded-lg shadow p-6 space-y-6">

      {/* Platform Management */}
      {user?.role === 'admin' && (
        <div className="pt-4">
          <div className="flex items-center gap-2 mb-2">
            <Settings size={18} className="text-blue-700" />
            <h3 className="text-md font-semibold text-gray-700">Platform Management</h3>
          </div>
          <div className="border-t border-gray-200 my-4" />
      
          <div className="grid grid-cols-3 gap-3 mb-4">
            {/* Manage Users */}
            <Link
              to="/users"
              className="inline-flex items-center justify-center px-3 py-1.5 border border-blue-200 bg-blue-50 text-blue-700 rounded font-medium hover:bg-blue-100 transition"
            >
              <Users size={16} className="mr-1" />
              Manage Users
            </Link>
            {/* Add test data */}
            <button
              className="inline-flex items-center justify-center px-3 py-1.5 border border-green-200 bg-green-50 text-green-700 rounded font-medium hover:bg-green-100 transition"
              onClick={async () => {
                try {
                  const res = await fetch('/api/dev/seed', { method: 'POST' });
                  if (!res.ok) throw new Error();
                  alert('Test data added!');
                } catch {
                  alert('Error adding test data');
                }
              }}
            >
              <Plus size={16} className="mr-1" />
              Add test data
            </button>
            {/* Remove test data */}
            <button
              className="inline-flex items-center justify-center px-3 py-1.5 border border-red-200 bg-red-50 text-red-700 rounded font-medium hover:bg-red-100 transition"
              onClick={async () => {
                try {
                  const res = await fetch('/api/dev/clean', { method: 'DELETE' });
                  if (!res.ok) throw new Error();
                  alert('Test data removed!');
                } catch {
                  alert('Error removing test data');
                }
              }}
            >
              <Trash size={16} className="mr-1" />
              Remove test data
            </button>
            {/* Create Backup Now */}
            <button
              className="inline-flex items-center justify-center px-3 py-1.5 border border-green-200 bg-green-50 text-green-700 rounded font-medium hover:bg-green-100 transition"
              onClick={async () => {
                try {
                  const res = await fetch('/api/backup/now', { method: 'POST' });
                  if (!res.ok) throw new Error();
                  alert('Backup created!');
                } catch {
                  alert('Error creating backup');
                }
              }}
            >
              <Database size={16} className="mr-1" />
              Create Backup Now
            </button>
            {/* Backup Schedule with two icons */}
            <button
              className="inline-flex items-center justify-center px-3 py-1.5 border border-blue-200 bg-blue-50 text-blue-700 rounded font-medium hover:bg-blue-100 transition"
              onClick={() => setShowSchedule(!showSchedule)}
            >
              <Calendar size={16} className="mr-1" />
              <Database size={16} className="mr-1" />
              Backup Schedule
            </button>
            {/* Espacio vacío para balancear el grid */}
            <div />
          </div>
            
          {/* Backup Schedule Form */}
          {showSchedule && (
            <form
              onSubmit={async (e) => {
                e.preventDefault();
                try {
                  const res = await fetch('/api/backup/schedule', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ days: scheduleDays, time: scheduleTime }),
                  });
                  if (!res.ok) throw new Error();
                  alert('Backup schedule saved!');
                  setShowSchedule(false);
                } catch {
                  alert('Error scheduling backups');
                }
              }}
              className="flex flex-col gap-4 bg-gray-50 rounded p-4 mt-2"
            >
              <div className="flex items-center gap-2">
                <span className="font-medium">Days:</span>
                {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].map((d) => (
                  <label key={d} className="flex items-center gap-1">
                    <input
                      type="checkbox"
                      name="days"
                      value={d}
                      className="accent-blue-700"
                      checked={scheduleDays.includes(d)}
                      onChange={e => {
                        if (e.target.checked) {
                          setScheduleDays([...scheduleDays, d]);
                        } else {
                          setScheduleDays(scheduleDays.filter(day => day !== d));
                        }
                      }}
                    />
                    {d}
                  </label>
                ))}
              </div>
              <div className="flex items-center gap-2">
                <label htmlFor="time" className="font-medium">
                  Time:
                </label>
                <input
                  type="time"
                  id="time"
                  name="time"
                  className="border px-2 py-1 rounded"
                  required
                  value={scheduleTime}
                  onChange={e => setScheduleTime(e.target.value)}
                />
              </div>
              <button
                type="submit"
                className="bg-blue-700 hover:bg-blue-800 text-white px-3 py-1 rounded self-start"
              >
                Save schedule
              </button>
            </form>
          )}
        </div>
      )}
        
      <div className={`pt-4${showManageUsers ? ' border-t mt-6' : ''}`}>
        <div className="flex items-center gap-2 mb-2">
          <User size={20} className="text-purple-600" />
          <h3 className="text-md font-semibold text-gray-700">Account Info</h3>
        </div>
        <Link
          to="/account"
          className="inline-flex items-center px-3 py-1.5 border border-blue-200 bg-blue-50 text-blue-700 rounded font-medium shadow hover:bg-blue-100 transition"
        >
          Edit Profile
        </Link>
      </div>

        <div className="pt-4 border-t mt-6">
          <div className="flex items-center gap-2 mb-2">
            <Layers size={18} className="text-blue-600" />
            <h3 className="text-md font-semibold text-gray-700">Categories</h3>
          </div>
            <Link
              to="/categories"
              className="inline-flex items-center px-3 py-1.5 border border-blue-200 bg-blue-50 text-blue-700 rounded font-medium shadow hover:bg-blue-100 transition"
            >
              <FolderPlus size={16} className="mr-1" />
              Manage Categories
            </Link>
        </div>

        <div className="pt-6">
          <div className="flex items-center gap-2 mb-2 border-t pt-4">
            <Calendar size={18} className="text-green-600" />
            <h3 className="text-md font-semibold text-gray-700">Years</h3>
          </div>
          <div className="flex gap-2">
            <button
              className="inline-flex items-center px-3 py-1.5 border border-green-200 bg-green-50 text-green-700 rounded font-medium shadow hover:bg-green-100 transition"
              onClick={() => { setAction('add'); setShowYearModal(true); setErrorMessage(''); setSuccessMessage(''); }}
            >
              <CalendarPlus size={16} className="mr-1" />
              Add Year
            </button>
            <button
              className="inline-flex items-center px-3 py-1.5 border border-red-200 bg-red-50 text-red-700 rounded font-medium shadow hover:bg-red-100 transition"
              onClick={() => { setAction('delete'); setShowYearModal(true); setErrorMessage(''); setSuccessMessage(''); }}
            >
              <CalendarMinus size={16} className="mr-1" />
              Delete Year
            </button>
          </div>
          {successMessage && <p className="text-sm text-green-600 mt-2">{successMessage}</p>}
        </div>

        <div/>

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