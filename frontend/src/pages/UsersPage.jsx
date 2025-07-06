import { useEffect, useState } from 'react';
import useAuthToken from '../hooks/useAuthToken';
import { KeyRound, Trash2 } from 'lucide-react';
import Modal from '../components/common/Modal';

export default function UsersPage() {
  const token = useAuthToken();
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);

  // Obtener usuarios
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
        setUsers(data.map(u => ({
          ...u,
          active: u.active === true || u.active === 1 || u.active === '1'
        })));
        setLoading(false);
      })
      .catch(() => {
        setError('No se pudo cargar la lista de usuarios');
        setLoading(false);
      });
  }, [token]);

  // Obtener roles
  useEffect(() => {
    if (!token) return;
    fetch('/api/roles', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setRoles(data))
      .catch(() => setRoles([]));
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

  const handleChangeRole = async (user, newRoleId) => {
    try {
      const res = await fetch(`/api/users/${user.id}/role`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ role_id: newRoleId })
      });
      if (!res.ok) throw new Error();
      setUsers(users.map(u =>
        u.id === user.id
          ? {
              ...u,
              role_id: parseInt(newRoleId),
              role: roles.find(r => r.id === parseInt(newRoleId))?.name
            }
          : u
      ));
    } catch {
      alert('No se pudo cambiar el rol del usuario');
    }
  };

  const handleResetPassword = (user) => {
    // Aquí puedes implementar la lógica real
    alert(`Restablecer contraseña de ${user.username}`);
  };

  const handleDeleteUser = (user) => {
    setUserToDelete(user);
    setShowDeleteModal(true);
  };

  if (loading) return <div className="p-4">Cargando usuarios...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;

  return (
    <>
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
                  <td className="py-2 px-4">
                    <select
                      value={u.role_id}
                      onChange={e => handleChangeRole(u, e.target.value)}
                      className="border rounded px-2 py-1"
                    >
                      {roles.map(r => (
                        <option key={r.id} value={r.id}>
                          {r.name}
                        </option>
                      ))}
                    </select>
                  </td>
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
                      className="text-blue-300 cursor-not-allowed"
                      disabled
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

      {/* Modal de confirmación para eliminar usuario */}
      {showDeleteModal && userToDelete && (
        <Modal
          title="Eliminar usuario"
          isOpen={showDeleteModal}
          onCancel={() => setShowDeleteModal(false)}
          onConfirm={async () => {
            try {
              const res = await fetch(`/api/users/${userToDelete.id}`, {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${token}` }
              });
              if (!res.ok) throw new Error();
              setUsers(users.filter(u => u.id !== userToDelete.id));
              setShowDeleteModal(false);
              setUserToDelete(null);
            } catch {
              alert('No se pudo eliminar el usuario');
            }
          }}
        >
          <div>
            ¿Seguro que quieres eliminar el usuario <b>{userToDelete.username}</b>?
          </div>
        </Modal>
      )}
    </>
  );
}
