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
  showNotification
}) {
  const handleDelete = useCallback(async () => {
    try {
      const success = await deleteRecord(endpoint, recordToDelete.id, setRecords, setNotification, token);
      if (success) {
        showNotification({ type: 'success', message: 'Record deleted successfully!' });
        setShowDeleteModal(false);
        setRecordToDelete(null);
      } else {
        showNotification({ type: 'error', message: 'Failed to delete record.' });
      }
    } catch (err) {
      showNotification({ type: 'error', message: 'Unexpected error while deleting record.' });
    }
  }, [endpoint, recordToDelete, setRecords, setNotification, token, setShowDeleteModal, setRecordToDelete]);

  return handleDelete;
}
