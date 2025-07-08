import { Settings, Users, Plus, Trash, Database, Calendar } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function PlatformManagementSection({
  showSchedule,
  setShowSchedule,
  scheduleDays,
  setScheduleDays,
  scheduleTime,
  setScheduleTime,
}) {
  return (
    <div className="pt-4">
      <div className="flex items-center gap-2 mb-2">
        <Settings size={18} className="text-blue-700" />
        <h3 className="text-md font-semibold text-gray-700">Platform Management</h3>
      </div>
      <div className="border-t border-gray-200 my-4" />

      <div className="grid grid-cols-3 gap-3 mb-4">
        <Link
          to="/users"
          className="inline-flex items-center justify-center px-3 py-1.5 border border-blue-200 bg-blue-50 text-blue-700 rounded font-medium hover:bg-blue-100 transition"
        >
          <Users size={16} className="mr-1" />
          Manage Users
        </Link>
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
        <button
          className="inline-flex items-center justify-center px-3 py-1.5 border border-blue-200 bg-blue-50 text-blue-700 rounded font-medium hover:bg-blue-100 transition"
          onClick={() => setShowSchedule(!showSchedule)}
        >
          <Calendar size={16} className="mr-1" />
          <Database size={16} className="mr-1" />
          Backup Schedule
        </button>
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
  );
}
