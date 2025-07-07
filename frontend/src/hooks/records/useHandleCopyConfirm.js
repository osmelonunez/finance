import { useCallback } from 'react';
import { addRecord } from '../../components/utils/records';
import { showNotification } from '../../components/utils/showNotification';

export default function useHandleCopyConfirm({
  copyState,
  setCopyState,
  field,
  isExpenses,
  endpoint,
  setRecords,
  setNotification,
  token,
  title
}) {
  const handleCopyConfirm = useCallback(async () => {
    const { record, targetMonth, targetYear } = copyState;

    if (!record || !targetMonth || !targetYear) {
      showNotification(setNotification, { type: 'error', message: 'Please select both month and year.' });
      return;
    }

    const newEntry = {
      name: record.name,
      [field]: record[field],
      month_id: targetMonth,
      year_id: targetYear,
      ...(isExpenses && { category_id: record.category_id }),
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
        showNotification(setNotification, { type: 'success', message: `${title.replace(/s$/, '')} copied successfully!` });
        setCopyState({ show: false, record: null, targetMonth: '', targetYear: '' });
      } else {
        showNotification(setNotification, { type: 'error', message: `Failed to copy ${title.toLowerCase()}.` });
      }
    } catch (err) {
      showNotification(setNotification, { type: 'error', message: `Unexpected error while copying ${title.toLowerCase()}.` });
    }
  }, [copyState, setCopyState, field, isExpenses, endpoint, setRecords, setNotification, token, title]);

  return handleCopyConfirm;
}
