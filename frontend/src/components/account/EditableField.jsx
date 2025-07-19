import { useState } from 'react';
import Modal from '../common/Modal';
import { isPasswordComplex } from '../utils/validation';
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

    if (type === 'password') {
      if (value !== confirmValue) {
        setError('Passwords do not match.');
        return;
      }
      if (!isPasswordComplex(value)) {
        setError('Password does not meet the minimum requirements.');
        return;
      }
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
          title={isEditing ? "Cancel editing" : `Edit ${label.toLowerCase()}`}
        >
          <Wrench size={18} className="text-yellow-600" />
        </button>

        {isEditing && (
          <button
            onClick={handleSaveClick}
            className="p-1 rounded-full hover:bg-green-100"
            title="Save"
          >
            <Check size={20} className="text-green-600" />
          </button>
        )}
      </h3>

      {isEditing && (
        <>
          <input
            type={type}
            value={value}
            placeholder={placeholder}
            onChange={onChange}
            className="w-full border rounded px-3 py-2"
          />

          {type === 'password' && (
            <input
              type="password"
              value={confirmValue}
              placeholder="Confirm password"
              onChange={e => setConfirmValue(e.target.value)}
              className="border rounded px-3 py-2 w-full mt-2"
            />
          )}

          {error && <p className="text-sm text-red-600 mt-1">{error}</p>}

          {children}

          <Modal
            title="Confirm update"
            isOpen={showConfirmModal}
            onConfirm={() => {
              onSave();
              setShowConfirmModal(false);
            }}
            onCancel={() => {
              setShowConfirmModal(false);
            }}
          >
            <p>Are you sure you want to update the password?</p>
          </Modal>
        </>
      )}
    </div>
  );
}
