import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { LogOut, Settings, Bell } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

export default function Navbar({ links = [] }) {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [showAlerts, setShowAlerts] = useState(false);
  const alertsButtonRef = useRef();

  // Demo: alerta con estado de leída/no leída
  const [alerts, setAlerts] = useState([
    { id: 1, message: "Monthly report available", date: "2024-07-11", read: false },
    { id: 2, message: "System update scheduled", date: "2024-07-13", read: false },
  ]);

  // Contador de alertas no leídas
  const unreadCount = alerts.filter(a => !a.read).length;

  const handleLogout = () => {
    logout();
    navigate('/');
  };

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

  // Al pasar el mouse por encima de una alerta, marcarla como leída
  const handleMouseEnterAlert = (alertId) => {
    setAlerts(prev =>
      prev.map(alert =>
        alert.id === alertId ? { ...alert, read: true } : alert
      )
    );
  };

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
                <div className="p-2 border-b font-semibold text-sm text-gray-600">
                  Alerts (Coming soon)
                </div>
                <ul className="max-h-60 overflow-y-auto">
                  {alerts.length === 0 && (
                    <li className="p-3 text-gray-400 text-sm text-center">No alerts</li>
                  )}
                  {alerts.map(alert => (
                    <li
                      key={alert.id}
                      onMouseEnter={() => !alert.read && handleMouseEnterAlert(alert.id)}
                      className={`p-3 border-b last:border-b-0 hover:bg-yellow-50 text-sm cursor-pointer transition-colors duration-150 ${
                        alert.read ? "opacity-60" : "font-medium"
                      }`}
                    >
                      <div>{alert.message}</div>
                      <div className="text-xs text-gray-400">{alert.date}</div>
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
