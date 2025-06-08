import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ username: '', password: '' });

  const from = location.state?.from?.pathname || '/';

  const handleSubmit = (e) => {
    e.preventDefault();
    if (login(form.username, form.password)) {
      navigate(from, { replace: true });
    } else {
      alert('Incorrect credentials');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-8 max-w-md mx-auto space-y-4">
      <h1 className="text-2xl mb-4">Login</h1>
      <input
        type="text"
        placeholder="Username"
        className="block w-full p-2 border"
        onChange={(e) => setForm({ ...form, username: e.target.value })}
      />
      <input
        type="password"
        placeholder="Password"
        className="block w-full p-2 border"
        onChange={(e) => setForm({ ...form, password: e.target.value })}
      />
      <div className="flex gap-4">
        <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">
          Login
        </button>
        <button
          type="button"
          onClick={() => navigate('/')}
          className="bg-gray-300 text-black px-4 py-2 rounded"
        >
          Return
        </button>
      </div>
    </form>
  );
}
