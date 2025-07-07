import { useCallback } from 'react';
import { addRecord } from '../../components/utils/records';
import { showNotification } from '../../components/utils/showNotification';

export default function useHandleAdd({
  endpoint,
  field,
  isExpenses,
  token,
  newRecord,
  setNewRecord,
  setShowAddModal,
  setError,
  setRecords,
  setNotification
}) {
  const handleAdd = useCallback(async () => {
    const requiredFields = ['name', field, 'month_id', 'year_id'];
    if (requiredFields.some(key => !newRecord[key] || newRecord[key].toString().trim() === '')) {
      showNotification(setNotification, { type: 'error', message: 'All fields are required.' });
      return;
    }

    try {
      const success = await addRecord(endpoint, newRecord, setRecords, setNotification, token);
      if (success) {
        showNotification(setNotification, { type: 'success', message: 'Record added successfully!' });
        setNewRecord({ name: '', [field]: '', month_id: '', year_id: '', ...(isExpenses && { category_id: '' }) });
        setShowAddModal(false);
        setError('');
      } else {
        showNotification(setNotification, { type: 'error', message: 'Failed to add record.' });
        setError('Failed to add record.');
      }
    } catch (err) {
      showNotification(setNotification, { type: 'error', message: 'Unexpected error while adding record.' });
      setError('Unexpected error while adding record.');
    }
  }, [endpoint, field, isExpenses, token, newRecord, setNewRecord, setShowAddModal, setError, setRecords, setNotification]);

  return handleAdd;
}
