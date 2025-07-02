// hooks/useFilteredExpenses.js

import { useMemo } from 'react';

export default function useFilteredExpenses(expenses, filters, search, sort) {
  return useMemo(() => {
    let result = [...expenses];

    if (filters.month_id)
      result = result.filter(e => parseInt(e.month_id) === parseInt(filters.month_id));
    if (filters.year_id)
      result = result.filter(e => parseInt(e.year_id) === parseInt(filters.year_id));
    if (filters.category_id)
      result = result.filter(e => e.category_id === parseInt(filters.category_id));
    if (search)
      result = result.filter(e => e.name.toLowerCase().includes(search.toLowerCase()));
    if (sort === 'name')
      result.sort((a, b) => a.name.localeCompare(b.name));
    if (sort === 'cost')
      result.sort((a, b) => parseFloat(b.cost) - parseFloat(a.cost));

    return result;
  }, [expenses, filters, search, sort]);
}
