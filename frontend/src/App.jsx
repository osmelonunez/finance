import RegisterPage from './pages/RegisterPage';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import ExpensesPage from './pages/ExpensesPage';
import IncomesPage from './pages/IncomesPage';
import CategoryManager from './pages/CategoryManager';
import DashboardPage from './pages/DashboardPage';
import Navbar from './components/Navbar';
import SavingsPage from './pages/SavingsPage';
import SettingsPage from './pages/SettingsPage';
import AccountPage from './pages/AccountPage';
import UsersPage from './pages/UsersPage';

const navLinks = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/expenses', label: 'Expenses' },
  { to: '/incomes', label: 'Incomes' },
  { to: '/savings', label: 'Savings' }
];

export default function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-100 text-gray-800">
        <Navbar links={navLinks} />
        <main className="max-w-6xl mx-auto px-4 py-6">
          <Routes>
  <Route path="/login" element={<LoginPage />} />
  <Route path="/register" element={<RegisterPage />} />
  <Route path="/" element={<HomePage />} />
  <Route path="/dashboard" element={<PrivateRoute><DashboardPage /></PrivateRoute>} />
  <Route path="/expenses" element={<PrivateRoute><ExpensesPage /></PrivateRoute>} />
  <Route path="/incomes" element={<PrivateRoute><IncomesPage /></PrivateRoute>} />
  <Route path="/savings" element={<PrivateRoute><SavingsPage /></PrivateRoute>} />
  <Route path="/categories" element={<PrivateRoute><CategoryManager /></PrivateRoute>} />
  <Route path="/settings" element={<PrivateRoute><SettingsPage /></PrivateRoute>} />
  <Route path="/account" element={<PrivateRoute><AccountPage /></PrivateRoute>} />
  <Route path="/users" element={<PrivateRoute><UsersPage /></PrivateRoute>} />
</Routes>
        </main>
      </div>
    </AuthProvider>
  );
}
