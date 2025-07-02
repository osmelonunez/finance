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
      setNotification({ type: 'success', message: successMsg });
      return true;
    } else {
      setNotification({ type: 'error', message: 'Failed to add expense.' });
      return false;
    }
  } catch (err) {
    console.error(err);
    setNotification({ type: 'error', message: 'Unexpected error while adding expense.' });
    return false;
  }
}
