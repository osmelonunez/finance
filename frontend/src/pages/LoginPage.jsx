import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

useEffect(() => {
  if (isAuthenticated && localStorage.getItem('token')) {
    console.log('Usuario autenticado, redirigiendo al dashboard');
    navigate('/dashboard');
  }
}, [isAuthenticated]);
  const location = useLocation();
  const [form, setForm] = useState({ username: '', password: '' });

  const from = location.state?.from?.pathname || '/';

  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await login(form.username, form.password);
    if (result === true) {
      navigate(from, { replace: true });
    } else {
      setError(result); // Muestra el mensaje real (inactivo o credenciales inválidas)
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
      <p className="text-sm text-gray-600">
        ¿No tienes una cuenta? <a href="/register" className="text-blue-600 hover:underline">Regístrate</a>
      </p>
      {error && (
        <div className="bg-red-100 text-red-700 p-2 rounded text-sm border border-red-300">
          {error}
        </div>
      )}
    </form>
  );
}
