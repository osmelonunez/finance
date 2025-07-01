import { useState, useEffect, useRef } from 'react';
import { Trash2, Wrench, Bell, PlusCircle, Check, X } from 'lucide-react';

export default function EmailManager() {
  const [emails, setEmails] = useState([]);
  const [emailError, setEmailError] = useState('');
  const [emailMessage, setEmailMessage] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [showAddInput, setShowAddInput] = useState(false);
  const [editingEmailId, setEditingEmailId] = useState(null);
  const [editedEmail, setEditedEmail] = useState('');
  const [emailToDelete, setEmailToDelete] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const emailInputRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    fetch('/api/emails', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(setEmails)
      .catch(() => {
        setEmailError('Error al cargar los correos');
        setTimeout(() => setEmailError(''), 2000);
      });
  }, []);

  const handleAddEmail = async () => {
    setEmailMessage('');
    setEmailError('');
    if (!newEmail || !newEmail.includes('@')) {
      setEmailError('Correo inválido');
      setTimeout(() => setEmailError(''), 2000);
      return;
    }

    const res = await fetch('/api/emails', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ email: newEmail })
    });

    if (res.ok) {
      const updated = await res.json();
      setEmails(updated);
      setEmailMessage('Correo agregado');
      setNewEmail('');
    } else {
      const data = await res.json();
      setEmailError(data.error || 'Error al agregar');
      setTimeout(() => setEmailError(''), 2000);
    }
  };

    const handleEditEmail = async () => {
      console.log('editando email con ID:', editingEmailId); // 👈 AQUÍ
    
      if (!editingEmailId || !editedEmail) return;
    
      const res = await fetch(`/api/emails/${editingEmailId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ email: editedEmail })
      });
  
      if (res.ok) {
        const updated = await res.json();
        setEmails(updated);
        setEditingEmailId(null);
        setEditedEmail('');
      }
    };


  const handleToggleNotifications = async (id, enabled) => {
    const res = await fetch(`/api/emails/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ notifications_enabled: enabled })
    });

    if (res.ok) {
      const updated = await res.json();
      setEmails(updated);
    }
  };

  const confirmDelete = async () => {
    if (!emailToDelete) return;
    const res = await fetch(`/api/emails/${emailToDelete.id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    });

    if (res.ok) {
      const updated = await res.json();
      setEmails(updated);
      setShowDeleteModal(false);
      setEmailToDelete(null);
    }
  };

  const startEditingEmail = (email) => {
    setEditingEmailId(email.id);
    setEditedEmail(email.email);
    setTimeout(() => emailInputRef.current?.focus(), 0);
  };

  return (
    <div className="mt-8">
      <h3 className="text-md font-semibold text-gray-700 mb-2">Correos asociados</h3>
      <ul className="text-sm text-gray-700">
        {emails.map(email => (
          <li key={email.id} className="py-1.5 flex justify-between items-center gap-3">
            <div className="flex flex-col">
              {editingEmailId === email.id ? (
                <>
                  <input
                    type="email"
                    ref={emailInputRef}
                    value={editedEmail}
                    onChange={e => setEditedEmail(e.target.value)}
                    className="border px-2 py-1 rounded"
                  />
                </>
              ) : (
                <>
                  <span className="font-medium hover:underline hover:text-blue-600 cursor-pointer transition-colors duration-200">{email.email}</span>
                  <span className="text-xs text-gray-500">
                    {email.is_primary ? 'Principal' : ''}
                  </span>
                </>
              )}
            </div>
            {!email.is_primary && (
              <div className="flex flex-row gap-2 items-center text-xs text-white">
                <button
                  onClick={() => handleToggleNotifications(email.id, !email.notifications_enabled)}
                  className="p-1 rounded-full hover:bg-gray-100"
                  title="Notificaciones"
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
                  title="Editar"
                >
                  <Wrench size={18} className="text-yellow-600" />
                  {editingEmailId === email.id && (
                    <button
                      onClick={handleEditEmail}
                      className="p-1 rounded-full hover:bg-green-100"
                      title="Guardar cambios"
                    >
                      <Check size={18} className="text-green-600" />
                    </button>
                  )}

                </button>
                <button
                  onClick={() => {
                    setEmailToDelete(email);
                    setShowDeleteModal(true);
                  }}
                  className="p-1 rounded-full hover:bg-red-100"
                  title="Eliminar"
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
          {!showAddInput && (
            <button
              onClick={() => setShowAddInput(true)}
              className="p-1 rounded-full hover:bg-gray-100"
              title="Agregar correo"
            >
              <PlusCircle size={20} className="text-green-600" />
            </button>
          )}
        </h3>
        {showAddInput && (
          <div className="flex gap-2 items-center animate-fade-in">
            <input
              type="email"
              placeholder="Correo secundario"
              className={`flex-1 border rounded px-3 py-2 ${emailError ? 'border-red-500' : 'border-gray-300'}`}
              value={newEmail}
              onChange={e => setNewEmail(e.target.value)}
            />
            <button
              onClick={handleAddEmail}
              className="p-1 rounded-full hover:bg-green-100"
              title="Guardar"
            >
              <Check size={20} className="text-green-600" />
            </button>
            <button
              onClick={() => {
                setShowAddInput(false);
                setNewEmail('');
              }}
              className="p-1 rounded-full hover:bg-red-100"
              title="Cancelar"
            >
              <X size={20} className="text-red-600" />
            </button>
          </div>
        )}
        {emailMessage && <p className="text-sm text-green-600 mt-2">{emailMessage}</p>}
        {emailError && <p className="text-sm text-red-600 mt-2">{emailError}</p>}
      </div>

      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-xl shadow-xl w-full max-w-md space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">¿Eliminar correo?</h3>
            <p className="text-gray-600">¿Estás seguro que deseas eliminar <strong>{emailToDelete?.email}</strong>?</p>
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowDeleteModal(false)} className="px-4 py-2 border rounded text-gray-600 hover:bg-gray-100">
                Cancelar
              </button>
              <button onClick={confirmDelete} className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
