import { useEffect, useState } from 'react';
import { TransitionGroup, CSSTransition } from 'react-transition-group';
import EditableField from '../components/account/EditableField';
import PasswordRequirements from '../components/account/PasswordRequirements';
import EmailManager from '../components/account/EmailManager';
import Notification from '../components/common/Notification';
import Loader from '../components/common/Loader';
import ErrorMessage from '../components/common/ErrorMessage';
import Modal from '../components/common/Modal';
import useAuthToken from '../components/hooks/useAuthToken';
import useTokenExpiration from '../components/hooks/useTokenExpiration';
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

      {/* Avisos de expiración */}
      <TransitionGroup className="fixed bottom-4 right-4 flex flex-col space-y-2 z-50">
        {warnings.map((msg) => (
          <CSSTransition key={msg} timeout={300} classNames="toast">
            <div
              className="bg-yellow-300 text-yellow-900 p-4 rounded shadow-lg cursor-pointer"
              onClick={() => removeWarning(msg)}
              role="alert"
            >
              {msg}
            </div>
          </CSSTransition>
        ))}
      </TransitionGroup>

      <Notification
        type="success"
        message={message}
        onClose={() => setMessage('')}
      />
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

      {/* Agrega estos estilos CSS para animar los avisos */}
      <style>{`
        .toast-enter {
          opacity: 0;
          transform: translateY(100%);
        }
        .toast-enter-active {
          opacity: 1;
          transform: translateY(0);
          transition: opacity 300ms, transform 300ms;
        }
        .toast-exit {
          opacity: 1;
          transform: translateY(0);
        }
        .toast-exit-active {
          opacity: 0;
          transform: translateY(-100%);
          transition: opacity 300ms, transform 300ms;
        }
      `}</style>
    </div>
  );
}
