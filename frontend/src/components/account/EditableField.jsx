import { useState } from 'react';
import Modal from '../common/Modal';
import { Wrench, Check } from 'lucide-react';

export default function EditableField({
  label,
  value,
  onChange,
  onSave,
  isEditing,
  setIsEditing,
  type = 'text',
  placeholder = '',
  children = null
}) {
  const [confirmValue, setConfirmValue] = useState('');
  const [error, setError] = useState('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const handleSaveClick = () => {
    setError('');

    if (type === 'password' && value !== confirmValue) {
      setError('Las contraseñas no coinciden.');
      return;
    }

    if (type === 'password') {
      setShowConfirmModal(true);
    } else {
      onSave();
    }
  };

  const cancelEdit = () => {
    setIsEditing(false);
    setError('');
    setConfirmValue('');
    setShowConfirmModal(false);
  };

  return (
    <div className="mt-4">
      <h3 className="text-md font-semibold text-gray-700 mb-1 flex items-center gap-2">
        <span>{label}</span>
        <button
          onClick={() => {
            if (isEditing) cancelEdit();
            else setIsEditing(true);
          }}
          className="p-1 rounded-full hover:bg-gray-100"
          title={isEditing ? `Cancelar edición` : `Editar ${label.toLowerCase()}`}
        >
          <Wrench size={18} className="text-yellow-600" />
        </button>
      </h3>

      {isEditing && (
        <>
          <div className="flex gap-2 items-center mb-2">
            <input
              type={type}
              value={value}
              placeholder={placeholder}
              onChange={onChange}
              className="flex-1 border rounded px-3 py-2"
            />
            <button
              onClick={handleSaveClick}
              className="p-1 rounded-full hover:bg-green-100"
              title="Guardar"
            >
              <Check size={20} className="text-green-600" />
            </button>
          </div>

          {type === 'password' && (
            <input
              type="password"
              value={confirmValue}
              placeholder="Confirmar contraseña"
              onChange={e => setConfirmValue(e.target.value)}
              className="border rounded px-3 py-2 w-full"
            />
          )}

          {error && <p className="text-sm text-red-600 mt-1">{error}</p>}

          {children}

          <Modal
            title="Confirmar actualización"
            isOpen={showConfirmModal}
            onConfirm={() => {
              onSave();
              setShowConfirmModal(false);
            }}
            onCancel={() => {
              setShowConfirmModal(false);
            }}
          >
            <p>¿Estás seguro que deseas actualizar la contraseña?</p>
          </Modal>
        </>
      )}
    </div>
  );
}
