
import { useMemo } from 'react';

export default function useFilteredRecords(records, filters, search, sort, field) {
  return useMemo(() => {
    let result = [...records];

    if (filters.month_id)
      result = result.filter(r => parseInt(r.month_id) === parseInt(filters.month_id));
    if (filters.year_id)
      result = result.filter(r => parseInt(r.year_id) === parseInt(filters.year_id));
    if (filters.category_id && field === 'cost')  // Solo para gastos
      result = result.filter(r => parseInt(r.category_id) === parseInt(filters.category_id));
    if (search)
      result = result.filter(r => r.name.toLowerCase().includes(search.toLowerCase()));

    if (sort === 'name') {
      result.sort((a, b) => a.name.localeCompare(b.name));
    } else if (sort === field) {
      result.sort((a, b) => parseFloat(b[field]) - parseFloat(a[field]));
    } else if (sort === 'year') {
      result.sort((a, b) => parseInt(b.year_id) - parseInt(a.year_id));
    } else if (sort === 'month') {
      result.sort((a, b) => parseInt(b.month_id) - parseInt(a.month_id));
    } else {
      result.sort((a, b) => {
        const yearDiff = parseInt(a.year_id) - parseInt(b.year_id);
        if (yearDiff !== 0) return yearDiff;

        const monthDiff = parseInt(a.month_id) - parseInt(b.month_id);
        if (monthDiff !== 0) return monthDiff;

        return a.name.localeCompare(b.name);
      });
    }

    return result;
  }, [records, filters, search, sort, field]);
}
