import { Wrench, Check } from 'lucide-react';
import { useState } from 'react';

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

  const reset = () => {
    setIsEditing(false);
    setConfirmValue('');
    setError('');
    setShowConfirmModal(false);
  };

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
      reset();
    }
  };

  const confirmPasswordSave = async () => {
    await onSave();
    reset();
  };

  return (
    <div className="mt-4">
      <h3 className="text-md font-semibold text-gray-700 mb-1 flex items-center gap-2">
        <span>{label}</span>
        <div className="flex items-center gap-1">
          <button
            onClick={() => {
              if (isEditing) reset();
              else setIsEditing(true);
            }}
            className="p-1 rounded-full hover:bg-gray-100"
            title={isEditing ? `Cancelar edición` : `Editar ${label.toLowerCase()}`}
          >
            <Wrench size={18} className="text-yellow-600" />
          </button>
          {isEditing && (
            <button
              onClick={handleSaveClick}
              className="p-1 rounded-full hover:bg-green-100"
              title="Guardar"
            >
              <Check size={18} className="text-green-600" />
            </button>
          )}
        </div>
      </h3>

      {isEditing && (
        <div className="animate-fade-in">
          <div className="mb-2 space-y-2">
            <input
              type={type}
              className="w-full border rounded px-3 py-2"
              value={value}
              placeholder={placeholder}
              onChange={onChange}
            />
            {type === 'password' && (
              <input
                type="password"
                className="w-full border rounded px-3 py-2"
                value={confirmValue}
                placeholder="Confirmar contraseña"
                onChange={e => setConfirmValue(e.target.value)}
              />
            )}
          </div>
          {error && <p className="text-sm text-red-600 mt-1">{error}</p>}
          {children}
        </div>
      )}

      {showConfirmModal && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-xl shadow-xl w-full max-w-md space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">¿Actualizar contraseña?</h3>
            <p className="text-gray-600">¿Estás seguro que deseas actualizar la contraseña?</p>
            <div className="flex justify-end gap-2">
              <button
                onClick={reset}
                className="px-4 py-2 border rounded text-gray-600 hover:bg-gray-100"
              >
                Cancelar
              </button>
              <button
                onClick={confirmPasswordSave}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Confirmar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
