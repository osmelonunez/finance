import { useEffect, useState } from 'react';
import useAuthToken from '../hooks/useAuthToken';
import { KeyRound, Trash2 } from 'lucide-react';

export default function UsersPage() {
  const token = useAuthToken();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    setLoading(true);

    fetch('/api/users', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => {
        if (!res.ok) throw new Error('No autorizado');
        return res.json();
      })
      .then(data => {
        setUsers(data);
        setLoading(false);
      })
      .catch(() => {
        setError('No se pudo cargar la lista de usuarios');
        setLoading(false);
      });
  }, [token]);

  const handleToggleStatus = async (user) => {
    try {
      const res = await fetch(`/api/users/${user.id}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ active: !user.active })
      });
      if (!res.ok) throw new Error();
      setUsers(users.map(u =>
        u.id === user.id ? { ...u, active: !user.active } : u
      ));
    } catch {
      alert('No se pudo cambiar el estado del usuario');
    }
  };

  const handleResetPassword = (user) => {
    alert(`Restablecer contraseña de ${user.username}`);
  };

  const handleDeleteUser = async (user) => {
    if (!window.confirm(`¿Eliminar usuario ${user.username}?`)) return;
    try {
      const res = await fetch(`/api/users/${user.id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error();
      setUsers(users.filter(u => u.id !== user.id));
    } catch {
      alert('No se pudo eliminar el usuario');
    }
  };

  if (loading) return <div className="p-4">Cargando usuarios...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-semibold mb-6 text-blue-700 flex items-center gap-2">
        🧑‍💼 Users Management
      </h2>
      <div className="overflow-x-auto rounded shadow">
        <table className="min-w-full bg-white border">
          <thead>
            <tr className="bg-gray-100 text-gray-700">
              <th className="py-2 px-4 border-b">Username</th>
              <th className="py-2 px-4 border-b">Role</th>
              <th className="py-2 px-4 border-b">Status</th>
              <th className="py-2 px-4 border-b">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="text-center hover:bg-gray-50 transition">
                <td className="py-2 px-4">{u.username}</td>
                <td className="py-2 px-4">{u.role}</td>
                <td className="py-2 px-4">
                  <input
                    type="checkbox"
                    checked={u.active}
                    onChange={() => handleToggleStatus(u)}
                    className="w-5 h-5 accent-blue-600"
                  />
                </td>
                <td className="py-2 px-4 flex justify-center gap-3">
                  <button
                    title="Restablecer contraseña"
                    onClick={() => handleResetPassword(u)}
                    className="text-blue-700 hover:text-blue-900"
                  >
                    <KeyRound size={18} />
                  </button>
                  <button
                    title="Eliminar usuario"
                    onClick={() => handleDeleteUser(u)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <Trash2 size={18} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
