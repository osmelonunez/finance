import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../auth/AuthContext';
import { LogOut, Settings, Bell } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

export default function Navbar({ links = [] }) {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [showAlerts, setShowAlerts] = useState(false);
  const alertsButtonRef = useRef();
  const [alerts, setAlerts] = useState([]);

  // Helper para traer alertas reales
  const fetchAlerts = async () => {
    try {
      const res = await fetch('/api/alerts', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await res.json();

      // Filtra: no resueltas y due_date hoy o anterior (o sin due_date)
      const today = new Date().toISOString().slice(0, 10);
      const filtered = data.filter(
        alert =>
          !alert.resolved &&
          (!alert.due_date || alert.due_date.slice(0, 10) <= today)
      );
      setAlerts(filtered);
    } catch (err) {
      setAlerts([]); // En caso de error, lista vacía
    }
  };

  // Fetch al montar y cada minuto
  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 60000); // 1 minuto = 60,000 ms
    return () => clearInterval(interval);
  }, []);

  // Actualiza al abrir la campana (por si hay cambios de otra pestaña)
  useEffect(() => {
    if (showAlerts) fetchAlerts();
  }, [showAlerts]);

  // Cierra dropdown si haces click fuera
  useEffect(() => {
    if (!showAlerts) return;
    function handleClick(e) {
      if (alertsButtonRef.current && !alertsButtonRef.current.contains(e.target)) {
        setShowAlerts(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [showAlerts]);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const unreadCount = alerts.length;

  return (
    <nav className="bg-white text-gray-800 py-4 shadow-md">
      <div className="max-w-6xl mx-auto flex justify-between items-center px-4">
        <div className="flex gap-6">
          {links.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className="px-4 py-2 rounded-full hover:bg-gray-100 hover:text-blue-600 transition-colors duration-300 font-medium"
            >
              {link.label}
            </Link>
          ))}
        </div>
        <div className="flex items-center gap-4">
          {/* ALERT ICON & DROPDOWN */}
          <div className="relative" ref={alertsButtonRef}>
            <button
              onClick={() => setShowAlerts((prev) => !prev)}
              className="text-gray-600 hover:text-yellow-600 flex items-center relative"
              title="Alerts"
            >
              <Bell size={20} />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs px-1 rounded-full">
                  {unreadCount}
                </span>
              )}
            </button>
            {showAlerts && (
              <div className="absolute right-0 mt-2 w-64 bg-white border rounded-lg shadow-lg z-50">
                <button
                  onClick={() => {
                    setShowAlerts(false);
                    navigate('/alerts');
                  }}
                  className="w-full text-left p-2 border-b font-semibold text-sm text-blue-700 hover:bg-blue-50 transition"
                  style={{ outline: 'none' }}
                >
                  Manage alerts
                </button>
                <ul className="max-h-60 overflow-y-auto">
                  {alerts.length === 0 && (
                    <li className="p-3 text-gray-400 text-sm text-center">No alerts</li>
                  )}
                  {alerts.map(alert => (
                    <li
                      key={alert.id}
                      className="p-3 border-b last:border-b-0 hover:bg-yellow-50 text-sm cursor-pointer transition-colors duration-150"
                    >
                      <div>{alert.message}</div>
                      <div className="text-xs text-gray-400">
                        {alert.due_date
                          ? `Target date: ${alert.due_date.slice(0,10)}`
                          : (alert.created_at ? `Created: ${alert.created_at.slice(0,10)}` : "")}
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
          {/* SETTINGS */}
          <Link
            to="/settings"
            className="text-gray-600 hover:text-black flex items-center gap-1"
          >
            <Settings size={18} />
          </Link>
          {/* LOGOUT */}
          <button
            onClick={handleLogout}
            className="px-4 py-2 rounded-full text-red-500 border border-transparent hover:border-red-500 hover:bg-red-50 transition-all flex items-center gap-2"
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
