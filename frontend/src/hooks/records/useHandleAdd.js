export default function useHandleAdd({
  endpoint,
  field,
  isExpenses,
  token,
  newRecord,
  setNewRecord,
  setShowAddModal,
  setRecords,
  showNotification
}) {
  return async () => {
    if (!newRecord.name || !newRecord[field]) {
      showNotification({ type: 'error', message: 'All fields are required.' }, 2000);
      return;
    }
    if (isExpenses && !newRecord.category_id) {
      showNotification({ type: 'error', message: 'Category is required.' }, 2000);
      return;
    }

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(newRecord),
      });

      if (res.ok) {
        const data = await res.json();
        setRecords(data);
        setShowAddModal(false);
        setNewRecord({ name: '', [field]: '', month_id: '', year_id: '', ...(isExpenses && { category_id: '' }) });
        showNotification({ type: 'success', message: 'Record added successfully.' }, 2000);
      } else {
        const data = await res.json();
        showNotification({ type: 'error', message: data.error || 'Failed to add record.' }, 2000);
      }
    } catch (err) {
      showNotification({ type: 'error', message: 'Network error.' }, 2000);
    }
  };
}
