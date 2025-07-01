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
  const handleSave = async () => {
    await onSave();
    // Opcional: cerrar edición tras guardar
    // setIsEditing(false);
  };

  return (
    <div className="mt-4">
      <h3 className="text-md font-semibold text-gray-700 mb-1 flex items-center gap-2">
        <span>{label}</span>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="p-1 rounded-full hover:bg-gray-100"
            title={isEditing ? `Cancelar edición` : `Editar ${label.toLowerCase()}`}
          >
            <Wrench size={18} className="text-yellow-600" />
          </button>
          {isEditing && (
            <button
              onClick={handleSave}
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
          <div className="mb-2">
            <input
              type={type}
              className="w-full border rounded px-3 py-2"
              value={value}
              placeholder={placeholder}
              onChange={onChange}
            />
          </div>
          {children}
        </div>
      )}
    </div>
  );
}
