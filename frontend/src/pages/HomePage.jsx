import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { ArrowDownCircle, ArrowUpCircle, PiggyBank } from "lucide-react";

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
            <rect x="3"  y="10" width="4" height="10" rx="1" fill="#10b981"/>
            <rect x="9" y="6"  width="4" height="14" rx="1" fill="#f59e42"/>
            <rect x="15" y="3"  width="4" height="17" rx="1" fill="#3b82f6"/>
          </svg>
          <span className="text-gray-800 font-medium">Dashboard</span>
        </Link>
        <Link
          to="/expenses"
          className="bg-white border border-gray-200 rounded-xl p-6 shadow-md w-44 flex flex-col items-center space-y-2 hover:shadow-lg transition"
        >
          <ArrowDownCircle className="w-10 h-10 text-red-500" strokeWidth={2.2} />
          <span className="text-gray-800 font-medium">Expenses</span>
        </Link>
        <Link
          to="/incomes"
          className="bg-white border border-gray-200 rounded-xl p-6 shadow-md w-44 flex flex-col items-center space-y-2 hover:shadow-lg transition"
        >
          <ArrowUpCircle className="w-10 h-10 text-green-600" strokeWidth={2.2} />
          <span className="text-gray-800 font-medium">Incomes</span>
        </Link>
        <Link
          to="/savings"
          className="bg-white border border-gray-200 rounded-xl p-6 shadow-md w-44 flex flex-col items-center space-y-2 hover:shadow-lg transition"
        >
          <PiggyBank className="w-10 h-10 text-yellow-500" strokeWidth={2.2} />
          <span className="text-gray-800 font-medium">Savings</span>
        </Link>

      </div>
    </div>
  );
}
