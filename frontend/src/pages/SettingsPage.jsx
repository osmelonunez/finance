import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Layers, Calendar, Settings, Users, Plus, Trash, Database, FolderPlus, CalendarPlus, CalendarMinus, User } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';
import PlatformManagementSection from '../components/settings/PlatformManagementSection';
import YearModal from '../components/settings/YearModal';

export default function SettingsPage() {
  const [years, setYears] = useState([]);
  const [newYear, setNewYear] = useState('');
  const [showYearModal, setShowYearModal] = useState(false);
  const [action, setAction] = useState('add');
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [showSchedule, setShowSchedule] = useState(false);
  const [scheduleDays, setScheduleDays] = useState([]);
  const [scheduleTime, setScheduleTime] = useState('');
  const { user } = useAuth();
  const showPlatformManagement = user?.role === 'admin';
  const showCategoriesAndYears = user?.role === 'admin' || user?.role === 'editor';


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

    const token = localStorage.getItem('token'); // <--- TOKEN AQUÍ

    if (action === 'add') {
      if (years.some(y => y.value === parseInt(newYear))) {
        setErrorMessage('That year already exists.');
        return;
      }
      const res = await fetch('/api/years', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
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
      const res = await fetch(`/api/years/${idToDelete}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
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
      {showPlatformManagement && (
        <PlatformManagementSection
          showSchedule={showSchedule}
          setShowSchedule={setShowSchedule}
          scheduleDays={scheduleDays}
          setScheduleDays={setScheduleDays}
          scheduleTime={scheduleTime}
          setScheduleTime={setScheduleTime}
        />
      )}
        
      <div className="pt-4">
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

      {/* Categorías (solo admin o editor) */}
      {showCategoriesAndYears && (
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
      )}

      {/* Gestión de años (solo admin o editor) */}
      {showCategoriesAndYears && (
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
      )}

        <div/>
      </div>
      <YearModal
        isOpen={showYearModal}
        onClose={() => setShowYearModal(false)}
        action={action}
        newYear={newYear}
        setNewYear={setNewYear}
        years={years}
        errorMessage={errorMessage}
        successMessage={successMessage}
        onSubmit={handleYearAction}
      />
    </div>
  );
}
