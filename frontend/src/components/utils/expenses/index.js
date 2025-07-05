import { showNotification } from '../showNotification';
// utils/expenses/index.js

export async function addExpense(data, setExpenses, setNotification, successMsg = 'Expense added successfully!') {
  try {
    const res = await fetch('/api/expenses', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (res.ok) {
      const updated = await res.json();
      setExpenses(updated);
      showNotification(setNotification, { type: 'success', message: successMsg });
      return true;
    } else {
      showNotification(setNotification, { type: 'error', message: 'Failed to add expense.' });
      return false;
    }
  } catch (err) {
    console.error(err);
    showNotification(setNotification, { type: 'error', message: 'Unexpected error while adding expense.' });
    return false;
  }
}

export async function updateExpense(data, setExpenses, setNotification) {
  try {
    const res = await fetch(`/api/expenses/${data.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (res.ok) {
      const updated = await res.json();
      setExpenses(updated);
      showNotification(setNotification, { type: 'success', message: 'Expense updated successfully!' });
      return true;
    } else {
      showNotification(setNotification, { type: 'error', message: 'Failed to update expense.' });
      return false;
    }
  } catch (err) {
    console.error(err);
    showNotification(setNotification, { type: 'error', message: 'Unexpected error while updating expense.' });
    return false;
  }
}

export async function deleteExpense(id, setExpenses, setNotification) {
  try {
    const res = await fetch(`/api/expenses/${id}`, {
      method: 'DELETE',
    });

    if (res.ok) {
      const updated = await res.json();
      setExpenses(updated);
      showNotification(setNotification, { type: 'success', message: 'Expense deleted successfully.' });
      return true;
    } else {
      showNotification(setNotification, { type: 'error', message: 'Failed to delete expense.' });
      return false;
    }
  } catch (err) {
    console.error(err);
    showNotification(setNotification, { type: 'error', message: 'Unexpected error while deleting expense.' });
    return false;
  }
}
