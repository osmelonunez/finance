import { showNotification } from './showNotification';

export async function addRecord(endpoint, data, setRecords, setNotification, successMsg = 'Record added successfully!') {
  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (res.ok) {
      const updated = await res.json();
      setRecords(updated);
      //setNotification({ type: 'success', message: successMsg });
      showNotification(setNotification, { type: 'success', message: successMsg });
      return true;
    } else {
      //setNotification({ type: 'error', message: 'Failed to add record.' });
      showNotification(setNotification, { type: 'error', message: 'Failed to add record.' });
      return false;
    }
  } catch (err) {
    console.error(err);
    setNotification({ type: 'error', message: 'Unexpected error while adding record.' });
    return false;
  }
}

export async function updateRecord(endpoint, data, setRecords, setNotification) {
  try {
    const res = await fetch(`${endpoint}/${data.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (res.ok) {
      const updated = await res.json();
      setRecords(updated);
      setNotification({ type: 'success', message: 'Record updated successfully!' });
      return true;
    } else {
      setNotification({ type: 'error', message: 'Failed to update record.' });
      return false;
    }
  } catch (err) {
    console.error(err);
    setNotification({ type: 'error', message: 'Unexpected error while updating record.' });
    return false;
  }
}

export async function deleteRecord(endpoint, id, setRecords, setNotification) {
  try {
    const res = await fetch(`${endpoint}/${id}`, {
      method: 'DELETE'
    });

    if (res.ok) {
      const updated = await res.json();
      setRecords(updated);
      setNotification({ type: 'success', message: 'Record deleted successfully.' });
      return true;
    } else {
      setNotification({ type: 'error', message: 'Failed to delete record.' });
      return false;
    }
  } catch (err) {
    console.error(err);
    setNotification({ type: 'error', message: 'Unexpected error while deleting record.' });
    return false;
  }
}
