import { useCallback } from 'react';
import { updateRecord } from '../../components/utils/records';
import { isValidRecord } from '../../components/utils/validation';
import { showNotification } from '../../components/utils/showNotification';

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
}) {
  const handleEdit = useCallback(async () => {
    if (!isValidRecord(editingRecord, field)) {
      showNotification(setNotification, { type: 'error', message: 'Please fill out all fields.' });
      return;
    }

    try {
      const success = await updateRecord(endpoint, editingRecord, setRecords, setNotification, token);
      if (success) {
        showNotification(setNotification, { type: 'success', message: 'Record updated successfully!' });
        setShowEditModal(false);
        setEditingRecord(null);
        setError('');
      } else {
        showNotification(setNotification, { type: 'error', message: 'Failed to update record.' });
        setError('Failed to update record.');
      }
    } catch (err) {
      showNotification(setNotification, { type: 'error', message: 'Unexpected error while updating record.' });
      setError('Unexpected error while updating record.');
    }
  }, [endpoint, field, token, editingRecord, setEditingRecord, setShowEditModal, setError, setRecords, setNotification]);

  return handleEdit;
}
