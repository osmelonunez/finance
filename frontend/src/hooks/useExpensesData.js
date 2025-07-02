import { useState, useEffect } from 'react';

export default function useExpensesData() {
  const [expenses, setExpenses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [months, setMonths] = useState([]);
  const [years, setYears] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };

    Promise.all([
      fetch('/api/expenses', { headers }).then(res => res.json()),
      fetch('/api/categories', { headers }).then(res => res.json()),
      fetch('/api/months', { headers }).then(res => res.json()),
      fetch('/api/years', { headers }).then(res => res.json()),
    ])
    .then(([expensesData, categoriesData, monthsData, yearsData]) => {
      setExpenses(expensesData);
      setCategories(categoriesData.sort((a, b) => a.name.localeCompare(b.name)));
      setMonths(monthsData);
      setYears(yearsData);
    })
    .catch((err) => {
      console.error('Error loading expenses data:', err);
    })
    .finally(() => {
      setLoading(false);
    });
  }, []);

  return {
    expenses,
    setExpenses,
    categories,
    months,
    years,
    loading,
  };
}
