import { useEffect, useState } from 'react';
import { Wrench } from 'lucide-react';
import EditableField from '../components/account/EditableField';
import PasswordRequirements from '../components/account/PasswordRequirements';
import EmailManager from '../components/account/EmailManager';

export default function AccountPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [editingUsername, setEditingUsername] = useState(false);
  const [editingPassword, setEditingPassword] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    fetch('/api/me', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(userData => {
        setUsername(userData.username);
        setLoading(false);
      })
      .catch(() => {
        setError('Error al cargar los datos');
        setLoading(false);
      });
  }, []);

  const isPasswordComplex = (pwd) => {
    const complexityRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d]).{13,}$/;
    return complexityRegex.test(pwd);
  };

  const handleUpdate = async (field) => {
    setMessage('');
    setError('');

    if (field === 'password' && !isPasswordComplex(password)) {
      setError('La contraseña no cumple con los requisitos mínimos.');
      return;
    }

    const res = await fetch('/api/me', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ username, password })
    });

    if (res.ok) {
      setMessage('Actualizado correctamente');
      setTimeout(() => setMessage(''), 2000);
      setPassword('');
      if (field === 'username') setEditingUsername(false);
      if (field === 'password') setEditingPassword(false);
    } else {
      const data = await res.json();
      setError(data.error || 'Error al actualizar');
    }
  };

  if (loading) {
    return <div className="text-center py-10 text-gray-600">Cargando datos...</div>;
  }

  return (
    <div className="max-w-xl mx-auto p-6 space-y-6 bg-white rounded-xl shadow">
      <h2 className="text-xl font-bold text-gray-800">Mi cuenta</h2>

      <EditableField
        label="Usuario"
        value={username}
        onChange={e => setUsername(e.target.value)}
        onSave={() => handleUpdate('username')}
        isEditing={editingUsername}
        setIsEditing={setEditingUsername}
      />

      <EditableField
        label="Contraseña"
        type="password"
        placeholder="Nueva contraseña"
        value={password}
        onChange={e => setPassword(e.target.value)}
        onSave={() => handleUpdate('password')}
        isEditing={editingPassword}
        setIsEditing={setEditingPassword}
      >
        <PasswordRequirements password={password} />
      </EditableField>

      {message && <p className="text-sm text-green-600 mt-2">{message}</p>}
      {error && <p className="text-sm text-red-600 mt-2">{error}</p>}

      <EmailManager />
    </div>
  );
}
