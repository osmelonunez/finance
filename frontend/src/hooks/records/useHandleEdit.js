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
}) {
  const handleEdit = useCallback(async () => {
    if (!isValidRecord(editingRecord, field)) {
      setError('Please fill out all fields');
      return;
    }

    try {
      const success = await updateRecord(endpoint, editingRecord, setRecords, setNotification, token);
      console.log('✅ Update result:', success);

      if (success) {
        setShowEditModal(false);
        setEditingRecord(null);
        setError('');
      } else {
        setError('Failed to update record.');
      }
    } catch (err) {
      console.error('🔥 Error while updating record:', err);
      setError('Unexpected error during update.');
    }
  }, [endpoint, field, token, editingRecord, setEditingRecord, setShowEditModal, setError, setRecords, setNotification]);

  return handleEdit;
}
