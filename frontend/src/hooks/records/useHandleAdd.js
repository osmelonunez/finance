import { useCallback } from 'react';
import { addRecord } from '../../components/utils/records';

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
    console.log('🚀 Trying to add record:', newRecord);

    const requiredFields = ['name', field, 'month_id', 'year_id'];
    if (requiredFields.some(key => !newRecord[key] || newRecord[key].toString().trim() === '')) {
      console.warn('❌ Missing required fields:', newRecord);
      setError('All fields are required.');
      return;
    }

    try {
      const success = await addRecord(endpoint, newRecord, setRecords, setNotification, token);
      console.log('✅ Submission result:', success);

      if (success) {
        setNewRecord({ name: '', [field]: '', month_id: '', year_id: '', ...(isExpenses && { category_id: '' }) });
        setShowAddModal(false);
        setError('');
      } else {
        console.error('❌ addRecord returned false.');
        setError('Failed to add record.');
      }
    } catch (err) {
      console.error('🔥 Error while submitting record:', err);
      setError('Unexpected error during submission.');
    }
  }, [endpoint, field, isExpenses, token, newRecord, setNewRecord, setShowAddModal, setError, setRecords, setNotification]);

  return handleAdd;
}
