import { useCallback } from 'react';
import { updateRecord } from '../../components/utils/records';
import { isValidRecord } from '../../components/utils/validation';

export default function useHandleEdit({
  endpoint,
  field,
  token,
  editingRecord,
  setEditingRecord,
  setShowEditModal,
  setError,
  setRecords,
  setNotification,
  showNotification,
  afterSuccess, // <--- NUEVO
}) {
  const handleEdit = useCallback(async () => {
    if (!isValidRecord(editingRecord, field)) {
      showNotification({ type: 'error', message: 'Please fill out all fields.' });
      return;
    }

    try {
      const success = await updateRecord(endpoint, editingRecord, setRecords, setNotification, token);
      if (success) {
        showNotification({ type: 'success', message: 'Record updated successfully!' });
        setShowEditModal(false);
        setEditingRecord(null);
        setError('');
        if (afterSuccess) afterSuccess(); // <--- LLAMADA AL FINAL
      } else {
        showNotification({ type: 'error', message: 'Failed to update record.' });
        setError('Failed to update record.');
      }
    } catch (err) {
      showNotification({ type: 'error', message: 'Unexpected error while updating record.' });
      setError('Unexpected error while updating record.');
    }
  }, [
    endpoint,
    field,
    token,
    editingRecord,
    setEditingRecord,
    setShowEditModal,
    setError,
    setRecords,
    setNotification,
    showNotification,
    afterSuccess // <--- AGREGA AQUÍ
  ]);

  return handleEdit;
}
