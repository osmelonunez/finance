import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function HomePage() {
  const { logout } = useAuth();

  useEffect(() => {
    logout(); // Cerrar sesión automáticamente al visitar Home
  }, [logout]);

  return (
    <div className="absolute inset-0 bg-white flex flex-col justify-start items-center text-center pt-20 space-y-10">
      <h1 className="text-4xl font-bold text-gray-900">Finance Panel</h1>
      <p className="text-gray-500 text-lg">Manage your finances in one place.</p>
      <div className="grid gap-6 md:grid-cols-3">
        <Link
          to="/dashboard"
          className="bg-white border border-gray-200 rounded-xl p-6 shadow-md w-44 flex flex-col items-center space-y-2 hover:shadow-lg transition"
        >
          <svg className="w-10 h-10" viewBox="0 0 24 24" fill="none">
            <rect x="3" y="10" width="4" height="10" rx="1" fill="#f97316"/>
            <rect x="10" y="6" width="4" height="14" rx="1" fill="#10b981"/>
            <rect x="17" y="3" width="4" height="17" rx="1" fill="#3b82f6"/>
          </svg>
          <span className="text-gray-800 font-medium">Dashboard</span>
        </Link>
        <Link
          to="/expenses"
          className="bg-white border border-gray-200 rounded-xl p-6 shadow-md w-44 flex flex-col items-center space-y-2 hover:shadow-lg transition"
        >
          <svg className="w-10 h-10" viewBox="0 0 24 24" fill="#ef4444" xmlns="http://www.w3.org/2000/svg">
            <path d="M2 5C2 3.9 2.9 3 4 3H20C21.1 3 22 3.9 22 5V7H2V5ZM2 9H22V19C22 20.1 21.1 21 20 21H4C2.9 21 2 20.1 2 19V9ZM6 17H9V15H6V17Z" />
          </svg>
          <span className="text-gray-800 font-medium">Expenses</span>
        </Link>
        <Link
          to="/incomes"
          className="bg-white border border-gray-200 rounded-xl p-6 shadow-md w-44 flex flex-col items-center space-y-2 hover:shadow-lg transition"
        >
          <svg className="w-10 h-10" viewBox="0 0 24 24" fill="none">
            <path d="M12 3l-6 6h4v6h4V9h4l-6-6z" fill="#22c55e"/>
          </svg>
          <span className="text-gray-800 font-medium">Incomes</span>
        </Link>
      </div>
    </div>
  );
}
