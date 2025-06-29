
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function RegisterPage() {
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!form.username || !form.email || !form.password) {
      setError('Todos los campos son obligatorios');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(form.email)) {
      setError('Correo electrónico inválido');
      return;
    }

    const res = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    });

    if (res.ok) {
      setSuccess('Usuario registrado con éxito');
      setTimeout(() => navigate('/login'), 1500);
    } else {
      const data = await res.json();
      setError(data.error || 'Error en el registro');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-8 max-w-md mx-auto space-y-4">
      <h1 className="text-2xl mb-4">Registro</h1>

      <input
        type="text"
        placeholder="Nombre de usuario"
        className="block w-full p-2 border"
        value={form.username}
        onChange={(e) => setForm({ ...form, username: e.target.value })}
      />

      <input
        type="email"
        placeholder="Correo electrónico"
        className="block w-full p-2 border"
        value={form.email}
        onChange={(e) => setForm({ ...form, email: e.target.value })}
      />

      <input
        type="password"
        placeholder="Contraseña"
        className="block w-full p-2 border"
        value={form.password}
        onChange={(e) => setForm({ ...form, password: e.target.value })}
      />

      {success && <div className="bg-green-100 text-green-700 p-2 rounded text-sm border border-green-300">{success}</div>}

      {error && <div className="bg-red-100 text-red-700 p-2 rounded text-sm border border-red-300">{error}</div>}

      <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
        Registrarse
      </button>
    </form>
  );
}
