import { useState, useEffect } from "react";
import SimpleModal from '../common/SimpleModal';
import RecordInfoContent from './RecordInfoContent';
import RecordEditForm from './RecordEditForm';
import { Wrench, Trash2, RefreshCw } from 'lucide-react';

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
  handleEdit,
  handleDelete,
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);
  const [showRecurrentConfig, setShowRecurrentConfig] = useState(false);
  const [recurrenceType, setRecurrenceType] = useState(record?.recurrence_type || "months");
  const [recurrenceCount, setRecurrenceCount] = useState(record?.recurrence_count || 1);
  
const [editingRecord, setEditingRecord] = useState(record || {});
useEffect(() => {
  setEditingRecord(record || {});
}, [record]);

  useEffect(() => {
    setIsEditing(false);
    setIsConfirmingDelete(false);
    setShowRecurrentConfig(false);
    setRecurrenceType(record?.recurrence_type || "months");
    setRecurrenceCount(record?.recurrence_count || 1);
  }, [record]);

  let mainTitle = title;
  if (mainTitle && mainTitle.endsWith('s')) mainTitle = mainTitle.slice(0, -1);
  const detailsTitle = `${mainTitle} details`;

  // Save recurrence (calls handleEdit with recurrence fields)
  const saveRecurrentConfig = async () => {
    await handleEdit({
      ...record,
      is_recurrent: true,
      recurrence_type: recurrenceType,
      recurrence_count: recurrenceCount,
    });
    setShowRecurrentConfig(false);
  };

  return (
    <SimpleModal isOpen={isOpen} onClose={onClose} title={detailsTitle}>
      {/* Main details view with Recurrence icon */}
      {!isEditing && !isConfirmingDelete && !showRecurrentConfig && (
        <>
          <RecordInfoContent
            record={record}
            field={field}
            hasCategory={hasCategory}
          />
          <div className="flex justify-end mt-8 space-x-3">
            {/* Recurrence icon button */}
            <button
              onClick={() => setShowRecurrentConfig(true)}
              className="bg-teal-500 hover:bg-teal-600 text-white rounded-full p-2 shadow"
              title="Set recurrence"
            >
              <RefreshCw size={22} />
            </button>
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
      )}

      {/* Recurrence config view */}
      {showRecurrentConfig && (
        <div className="flex flex-col gap-4">
          <h3 className="text-lg font-bold">Recurrence Settings</h3>
          <div>
            <label className="font-semibold mr-2">Recurrence type:</label>
            <select
              value={recurrenceType}
              onChange={e => setRecurrenceType(e.target.value)}
              className="border rounded px-2 py-1"
            >
              <option value="months">By months</option>
              <option value="years">By years</option>
            </select>
          </div>
          <div>
            <label className="font-semibold mr-2">
              {recurrenceType === "months" ? "Number of months:" : "Number of years:"}
            </label>
            <input
              type="number"
              min="1"
              value={recurrenceCount}
              onChange={e => setRecurrenceCount(Number(e.target.value))}
              className="border rounded px-2 py-1 w-24"
            />
          </div>
          <div className="flex justify-end gap-3 mt-2">
            <button
              onClick={() => setShowRecurrentConfig(false)}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 rounded px-4 py-2"
            >
              Cancel
            </button>
            <button
              onClick={saveRecurrentConfig}
              className="bg-green-600 hover:bg-green-700 text-white rounded px-4 py-2"
            >
              Save
            </button>
          </div>
        </div>
      )}

      {/* Edit mode (stays as you had it) */}
{isEditing && (
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

      {/* Delete confirm */}
      {isConfirmingDelete && (
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
              onClick={async () => { await handleDelete(record); setIsConfirmingDelete(false); onClose(); }}
              className="bg-red-600 hover:bg-red-700 text-white rounded px-4 py-2"
            >
              Confirm Delete
            </button>
          </div>
        </div>
      )}
    </SimpleModal>
  );
}
