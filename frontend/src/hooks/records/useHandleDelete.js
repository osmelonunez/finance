import { useCallback } from 'react';
import { deleteRecord } from '../../components/utils/records';

export default function useHandleDelete({
  endpoint,
  recordToDelete,
  setRecords,
  setNotification,
  token,
  setShowDeleteModal,
  setRecordToDelete,
}) {
  const handleDelete = useCallback(async () => {
    try {
      const success = await deleteRecord(endpoint, recordToDelete.id, setRecords, setNotification, token);
      console.log('🗑️ Delete result:', success);

      if (success) {
        setShowDeleteModal(false);
        setRecordToDelete(null);
      } else {
        setNotification({ type: 'error', message: 'Failed to delete record.' });
      }
    } catch (err) {
      console.error('🔥 Error while deleting record:', err);
      setNotification({ type: 'error', message: 'Unexpected error while deleting record.' });
    }
  }, [endpoint, recordToDelete, setRecords, setNotification, token, setShowDeleteModal, setRecordToDelete]);

  return handleDelete;
}
