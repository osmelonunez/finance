import { useState, useEffect } from "react";
import SimpleModal from '../common/SimpleModal';
import RecordInfoContent from './RecordInfoContent';
import RecordEditForm from './RecordEditForm';
import { Wrench, Trash2 } from 'lucide-react';

export default function ViewRecordModal({
  isOpen,
  onClose,
  record,
  field,
  hasCategory,
  title,
  months = [],
  years = [],
  categories = [],
  handleEdit,   // función async para guardar cambios
  handleDelete, // función async para borrar el registro
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [editingRecord, setEditingRecord] = useState(record || {});
  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);

  useEffect(() => {
    setEditingRecord(record || {});
    setIsEditing(false);
    setIsConfirmingDelete(false); // Resetea la confirmación al cambiar registro/modal
  }, [record]);

  // Confirmar borrado y cerrar modal
  const confirmDelete = async () => {
    await handleDelete(record);   // tu función para borrar en la BD
    setIsConfirmingDelete(false);
    onClose();                   // cierra el modal después de borrar
  };

  // Manejar ESC para cerrar
  useEffect(() => {
    if (!isOpen) return;
    const handleEsc = (e) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [isOpen, onClose]);

  // Título limpio
  let mainTitle = title;
  if (mainTitle && mainTitle.endsWith('s')) {
    mainTitle = mainTitle.slice(0, -1);
  }
  const detailsTitle = `${mainTitle} details`;

  return (
    <SimpleModal isOpen={isOpen} onClose={onClose} title={detailsTitle}>
      {isConfirmingDelete ? (
        <div className="space-y-6">
          <div className="text-center text-xl font-semibold text-red-600">
            Are you sure you want to delete this record?
          </div>
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setIsConfirmingDelete(false)}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 rounded px-4 py-2"
            >
              Cancel
            </button>
            <button
              onClick={confirmDelete}
              className="bg-red-600 hover:bg-red-700 text-white rounded px-4 py-2"
            >
              Confirm Delete
            </button>
          </div>
        </div>
      ) : !isEditing ? (
        <>
          <RecordInfoContent
            record={record}
            field={field}
            hasCategory={hasCategory}
          />
          <div className="flex justify-end mt-8 space-x-3">
            <button
              onClick={() => setIsEditing(true)}
              className="bg-blue-500 hover:bg-blue-600 text-white rounded-full p-2 shadow"
              title="Edit"
            >
              <Wrench size={24} />
            </button>
            <button
              onClick={() => setIsConfirmingDelete(true)}
              className="bg-red-500 hover:bg-red-600 text-white rounded-full p-2 shadow"
              title="Delete"
            >
              <Trash2 size={24} />
            </button>
          </div>
        </>
      ) : (
        <>
          <RecordEditForm
            editingRecord={editingRecord}
            setEditingRecord={setEditingRecord}
            field={field}
            months={months}
            years={years}
            categories={categories}
            hasCategory={hasCategory}
          />
          <div className="flex justify-end mt-8 space-x-3">
            <button
              onClick={() => setIsEditing(false)}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 rounded px-4 py-2"
            >
              Cancel
            </button>
            <button
              onClick={async () => {
                await handleEdit(editingRecord);
                setIsEditing(false);
              }}
              className="bg-green-600 hover:bg-green-700 text-white rounded px-4 py-2"
            >
              Save
            </button>
          </div>
        </>
      )}
    </SimpleModal>
  );
}
