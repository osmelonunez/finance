import { useCallback } from 'react';
import { addRecord } from '../../components/utils/records';


export default function useHandleCopyConfirm({
  copyState,
  setCopyState,
  field,
  isExpenses,
  endpoint,
  setRecords,
  setNotification,
  token,
  title,
  showNotification
}) {
  const handleCopyConfirm = useCallback(async () => {
    const { record, targetMonth, targetYear } = copyState;

    if (!record || !targetMonth || !targetYear) {
      showNotification({ type: 'error', message: 'Please select both month and year.' });
      return;
    }

    const newEntry = {
      name: record.name,
      [field]: record[field],
      month_id: targetMonth,
      year_id: targetYear,
      ...(isExpenses && { category_id: record.category_id }),
      ...(isExpenses && { source: record.source }),
      created_by_user_id: record.created_by_user_id,
    };

    try {
      const success = await addRecord(
        endpoint,
        newEntry,
        setRecords,
        setNotification,
        token,
        `${title.replace(/s$/, '')} copied successfully!`
      );
      if (success) {
        showNotification({ type: 'success', message: `${title.replace(/s$/, '')} copied successfully!` });
        setCopyState({ show: false, record: null, targetMonth: '', targetYear: '' });
      } else {
        showNotification({ type: 'error', message: `Failed to copy ${title.toLowerCase()}.` });
      }
    } catch (err) {
      showNotification({ type: 'error', message: `Unexpected error while copying ${title.toLowerCase()}.` });
    }
  }, [copyState, setCopyState, field, isExpenses, endpoint, setRecords, setNotification, token, title]);

  return handleCopyConfirm;
}
