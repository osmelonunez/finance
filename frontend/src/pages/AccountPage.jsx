import { useEffect, useState } from 'react';
import EditableField from '../components/account/EditableField';
import PasswordRequirements from '../components/account/PasswordRequirements';
import EmailManager from '../components/account/EmailManager';
import Notification from '../components/common/Notification';
import Loader from '../components/common/Loader';
import ErrorMessage from '../components/common/ErrorMessage';
import Modal from '../components/common/Modal';
import useAuthToken from '../hooks/useAuthToken';
import useTokenExpiration from '../hooks/useTokenExpiration';
import TokenWarnings from '../components/common/TokenWarnings';
import { isPasswordComplex } from '../components/utils/validation';

export default function AccountPage() {
  const token = useAuthToken();
  const { warnings, removeWarning } = useTokenExpiration(token);

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [editingUsername, setEditingUsername] = useState(false);
  const [editingPassword, setEditingPassword] = useState(false);

  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [confirmAction, setConfirmAction] = useState(null);
  const [pendingField, setPendingField] = useState(null);
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    if (!token) return;

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
  }, [token]);

  const handleUpdate = async (field) => {
    if (!token) {
      setError('Token no disponible');
      return;
    }

    setMessage('');
    setError('');

    if (field === 'password' && !isPasswordComplex(password)) {
      setError('La contraseña no cumple con los requisitos mínimos.');
      return;
    }

    if (field === 'password') {
      setPendingField(field);
      setConfirmAction(() => async () => {
        const res = await fetch('/api/me', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({ username, password })
        });

        if (res.ok) {
          setMessage('Actualizado correctamente');
          setTimeout(() => setMessage(''), 2000);
          setPassword('');
          setEditingPassword(false);
        } else {
          const data = await res.json();
          setError(data.error || 'Error al actualizar');
        }
      });
      setShowConfirmModal(true);
    } else {
      const res = await fetch('/api/me', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ username, password })
      });

      if (res.ok) {
        setMessage('Actualizado correctamente');
        setTimeout(() => setMessage(''), 2000);
        if (field === 'username') setEditingUsername(false);
      } else {
        const data = await res.json();
        setError(data.error || 'Error al actualizar');
      }
    }
  };

  if (loading) {
    return <Loader />;
  }

  return (
    <div className="max-w-xl mx-auto p-6 space-y-6 bg-white rounded-xl shadow">
      <h2 className="text-xl font-bold text-gray-800">Mi cuenta</h2>

      <TokenWarnings warnings={warnings} onRemove={removeWarning} />

      {notification && (
        <Notification
          type={notification.type}
          message={notification.message}
          onClose={() => setNotification(null)}
        />
      )}

      <ErrorMessage message={error} />

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

      <EmailManager token={token} />

      <Modal
        title="Confirmar actualización"
        isOpen={showConfirmModal}
        onConfirm={() => {
          confirmAction();
          setShowConfirmModal(false);
        }}
        onCancel={() => {
          setShowConfirmModal(false);
          setPendingField(null);
        }}
      >
        <p>¿Estás seguro que deseas actualizar {pendingField}?</p>
      </Modal>
    </div>
  );
}
