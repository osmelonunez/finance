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
      <div className="grid gap-6 md:grid-cols-4">
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
        <Link
          to="/savings"
          className="bg-white border border-gray-200 rounded-xl p-6 shadow-md w-44 flex flex-col items-center space-y-2 hover:shadow-lg transition"
        >
          {/* Money bag and coin */}
          <svg className="w-10 h-10" viewBox="0 0 48 48" fill="none">
            {/* Bag */}
            <ellipse cx="24" cy="36" rx="10" ry="8" fill="#34d399"/>
            <path d="M24 12c-6 2-10 7-10 12v4c0 4.5 5 8 10 8s10-3.5 10-8v-4c0-5-4-10-10-12z" fill="#34d399" stroke="#059669" strokeWidth="2"/>
            {/* Neck of bag */}
            <rect x="19" y="16" width="10" height="5" rx="2.5" fill="#fbbf24" stroke="#b45309" strokeWidth="1"/>
            {/* Coin */}
            <circle cx="33" cy="36" r="5" fill="#fbbf24" stroke="#b45309" strokeWidth="2"/>
            <text x="33" y="39" textAnchor="middle" fontSize="8" fill="#b45309" fontWeight="bold">$</text>
          </svg>
          <span className="text-gray-800 font-medium">Savings</span>
        </Link>
      </div>
    </div>
  );
}
