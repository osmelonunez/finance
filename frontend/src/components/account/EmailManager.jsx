import { useState, useEffect, useRef } from 'react';
import { Trash2, Wrench, Bell, PlusCircle, Check } from 'lucide-react';
import Modal from '../common/Modal';
import { isEmailValid } from '../utils/validation';
import useAuthToken from '../../hooks/useAuthToken';
import { showNotification } from '../utils/showNotification';

export default function EmailManager() {
  const token = useAuthToken();

  const [emails, setEmails] = useState([]);
  const [newEmail, setNewEmail] = useState('');
  const [showAddInput, setShowAddInput] = useState(false);
  const [editingEmailId, setEditingEmailId] = useState(null);
  const [editedEmail, setEditedEmail] = useState('');
  const [emailToDelete, setEmailToDelete] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [inputTouched, setInputTouched] = useState(false);
  const emailInputRef = useRef(null);

  useEffect(() => {
    if (!token) return;

    fetch('/api/emails', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(setEmails)
      .catch(() => {
        showNotification({ type: 'error', message: 'Failed to load emails' }, 2000);
      });
  }, [token]);

  const handleAddEmail = async () => {
    setInputTouched(true);

    if (!newEmail || !isEmailValid(newEmail)) {
      showNotification({ type: 'error', message: 'Invalid email address' }, 2000);
      return;
    }

    const exists = emails.some(email => email.email.toLowerCase() === newEmail.toLowerCase());
    if (exists) {
      showNotification({ type: 'error', message: 'This email is already added.' }, 2000);
      return;
    }

    if (!token) {
      showNotification({ type: 'error', message: 'Token not available' }, 2000);
      return;
    }

    const res = await fetch('/api/emails', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ email: newEmail })
    });

    if (res.ok) {
      const updated = await res.json();
      setEmails(updated);
      showNotification({ type: 'success', message: 'Email added successfully' }, 2000);
      setNewEmail('');
      setShowAddInput(false);
      setInputTouched(false);
    } else {
      const data = await res.json();
      showNotification({ type: 'error', message: data.error || 'Failed to add email' }, 2000);
    }
  };

  const handleEditEmail = async () => {
    if (!editingEmailId || !editedEmail) return;
  
    if (!isEmailValid(editedEmail)) {
      showNotification({ type: 'error', message: 'Invalid email address' }, 2000);
      return;
    }
  
    const exists = emails.some(email =>
      email.email.toLowerCase() === editedEmail.toLowerCase() && email.id !== editingEmailId
    );
    if (exists) {
      showNotification({ type: 'error', message: 'This email is already added.' }, 2000);
      return;
    }
  
    if (!token) {
      showNotification({ type: 'error', message: 'Token not available' }, 2000);
      return;
    }
  
    // <-- NUEVO: toma el email original para no perder notificaciones_enabled
    const originalEmail = emails.find(e => e.id === editingEmailId);
  
    const res = await fetch(`/api/emails/${editingEmailId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        email: editedEmail,
        notifications_enabled: originalEmail.notifications_enabled // ¡Aquí!
      })
    });
  
    if (res.ok) {
      const updated = await res.json();
      setEmails(updated);
      setEditingEmailId(null);
      setEditedEmail('');
      showNotification({ type: 'success', message: 'Email updated successfully' }, 2000);
    } else {
      const data = await res.json();
      showNotification({ type: 'error', message: data.error || 'Failed to update email' }, 2000);
    }
  };

  const handleToggleNotifications = async (id, enabled) => {
    if (!token) {
      showNotification({ type: 'error', message: 'Token not available' }, 2000);
      return;
    }

    const res = await fetch(`/api/emails/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ notifications_enabled: enabled })
    });

    if (res.ok) {
      const updated = await res.json();
      setEmails(updated);
      showNotification({
        type: 'success',
        message: enabled ? 'Notifications enabled' : 'Notifications disabled'
      }, 2000);
    }
  };

  const confirmDelete = async () => {
    if (!emailToDelete) return;
    if (!token) {
      showNotification({ type: 'error', message: 'Token not available' }, 2000);
      return;
    }

    const res = await fetch(`/api/emails/${emailToDelete.id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    if (res.ok) {
      const updated = await res.json();
      setEmails(updated);
      setShowDeleteModal(false);
      setEmailToDelete(null);
      showNotification({ type: 'success', message: 'Email deleted successfully' }, 2000);
    } else {
      showNotification({ type: 'error', message: 'Failed to delete email' }, 2000);
    }
  };

  const startEditingEmail = (email) => {
    setEditingEmailId(email.id);
    setEditedEmail(email.email);
    setTimeout(() => emailInputRef.current?.focus(), 0);
  };

  const inputInvalid = !isEmailValid(newEmail) && inputTouched && showAddInput;

  return (
    <div className="mt-8">
      <h3 className="text-md font-semibold text-gray-700 mb-2">Associated emails</h3>
      <ul className="text-sm text-gray-700">
        {emails.map(email => (
          <li key={email.id} className="py-1.5 flex justify-between items-center gap-3">
            <div className="flex flex-col">
              {editingEmailId === email.id ? (
                <div className="flex items-center gap-2">
                  <input
                    type="email"
                    ref={emailInputRef}
                    value={editedEmail}
                    onChange={e => setEditedEmail(e.target.value)}
                    className="border px-2 py-1 rounded w-full"
                  />
                  <button
                    onClick={handleEditEmail}
                    className="p-1 rounded-full hover:bg-green-100"
                    title="Save changes"
                  >
                    <Check size={18} className="text-green-600" />
                  </button>
                </div>
              ) : (
                <>
                  <span className="font-medium hover:underline hover:text-blue-600 cursor-pointer transition-colors duration-200">{email.email}</span>
                  <span className="text-xs text-gray-500">
                    {email.is_primary ? 'Primary' : ''}
                  </span>
                </>
              )}
            </div>
            {!email.is_primary && (
              <div className="flex flex-row gap-2 items-center text-xs text-white">
                <button
                  onClick={() => handleToggleNotifications(email.id, !email.notifications_enabled)}
                  className="p-1 rounded-full hover:bg-gray-100"
                  title="Notifications"
                >
                  <Bell size={18} className={email.notifications_enabled ? 'text-green-600' : 'text-gray-400'} />
                </button>
                <button
                  onClick={() => {
                    if (editingEmailId === email.id) {
                      setEditingEmailId(null);
                      setEditedEmail('');
                    } else {
                      startEditingEmail(email);
                    }
                  }}
                  className="p-1 rounded-full hover:bg-yellow-100"
                  title="Edit"
                >
                  <Wrench size={18} className="text-yellow-600" />
                </button>
                <button
                  onClick={() => {
                    setEmailToDelete(email);
                    setShowDeleteModal(true);
                  }}
                  className="p-1 rounded-full hover:bg-red-100"
                  title="Delete"
                >
                  <Trash2 size={18} className="text-red-600" />
                </button>
              </div>
            )}
          </li>
        ))}
      </ul>

      <div className="mt-6">
        <h3 className="text-md font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                if (showAddInput) {
                  setShowAddInput(false);
                  setNewEmail('');
                  setInputTouched(false);
                } else {
                  setShowAddInput(true);
                }
              }}
              className="p-1 rounded-full hover:bg-gray-100"
              title={showAddInput ? 'Cancel' : 'Add email'}
            >
              <PlusCircle
                size={20}
                className={showAddInput ? 'text-yellow-600' : 'text-green-600'}
              />
            </button>

            {showAddInput && (
              <button
                onClick={handleAddEmail}
                className="p-1 rounded-full hover:bg-green-100"
                title="Save new email"
              >
                <Check size={20} className="text-green-600" />
              </button>
            )}
          </div>
        </h3>

        {showAddInput && (
          <div className="flex items-center animate-fade-in">
            <input
              type="email"
              placeholder="Secondary email"
              className={`border rounded px-3 py-2 max-w-xs w-full ${inputInvalid ? 'border-red-500' : 'border-gray-300'}`}
              value={newEmail}
              onChange={e => {
                setNewEmail(e.target.value);
                setInputTouched(true);
              }}
            />
            {inputInvalid && (
              <span className="ml-3 text-xs text-red-500">Enter a valid email address</span>
            )}
          </div>
        )}

      </div>

      <Modal
        title="Delete email?"
        isOpen={showDeleteModal}
        onConfirm={confirmDelete}
        onCancel={() => setShowDeleteModal(false)}
      >
        <p>Are you sure you want to delete <strong>{emailToDelete?.email}</strong>?</p>
      </Modal>
    </div>
  );
}
