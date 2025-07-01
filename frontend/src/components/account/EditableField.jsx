// components/EditableField.jsx
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
  return (
    <div className="mt-4">
      <h3 className="text-md font-semibold text-gray-700 mb-1 flex items-center gap-2">
        <span>{label}</span>
        <button
          onClick={() => setIsEditing(!isEditing)}
          className="p-1 rounded-full hover:bg-gray-100"
          title={isEditing ? `Cancelar edición` : `Editar ${label.toLowerCase()}`}
        >
          <Wrench size={18} className="text-yellow-600" />
        </button>
      </h3>

      {isEditing && (
        <div className="animate-fade-in">
          <div className="flex gap-2 items-center mb-2">
            <input
              type={type}
              className="flex-1 border rounded px-3 py-2"
              value={value}
              placeholder={placeholder}
              onChange={onChange}
            />
            <button
              onClick={onSave}
              className="p-1 rounded-full hover:bg-green-100"
              title="Guardar"
            >
              <Check size={20} className="text-green-600" />
            </button>
          </div>
          {children}
        </div>
      )}
    </div>
  );
}
