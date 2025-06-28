import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { LogOut, Settings } from 'lucide-react';

export default function Navbar({ links = [] }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
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
          <Link
            to="/settings"
            className="text-gray-600 hover:text-black flex items-center gap-1"
          >
            <Settings size={18} />
          </Link>
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