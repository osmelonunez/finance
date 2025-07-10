import { useEffect, useState } from 'react';

export default function FiltersBarRecords({
  filters,
  setFilters,
  sort,
  setSort,
  search,
  setSearch,
  months,
  years,
  onAdd,
  label = 'Record',
  type,
  categories = [],
  isViewer={isViewer}
}) {
  const isExpenses = type === 'expenses';

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const [sourceOptions, setSourceOptions] = useState([]);
  useEffect(() => {
  if (type === 'expenses') {
    fetch('/api/expenses/sources')
      .then(res => res.json())
      .then(data => setSourceOptions(data))
      .catch(err => setSourceOptions([])); // opcional: manejar error
  }
}, [type]);

  return (
    <div className="bg-white p-6 rounded-xl shadow space-y-4">
      <div className="flex flex-wrap gap-4 items-center">
        <select
          name="sort"
          value={sort}
          onChange={(e) => setSort(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="">Sort by</option>
          <option value="name">Name</option>
          <option value={isExpenses ? 'cost' : 'amount'}>{isExpenses ? 'Cost' : 'Amount'}</option>
          <option value="month">Month</option>
          <option value="year">Year</option>
          {isExpenses && <option value="category_id">Category</option>}
          <option value="">Default (Y-M-N)</option>
        </select>

        <input
          type="text"
          name="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name..."
          className="border rounded px-3 py-2 w-36"
        />

        <select
          name="month_id"
          value={filters.month_id}
          onChange={handleFilterChange}
          className="border rounded px-3 py-2"
        >
          <option value="">All Months</option>
          {months.map((m) => (
            <option key={m.id} value={m.id}>{m.name}</option>
          ))}
        </select>

        <select
          name="year_id"
          value={filters.year_id}
          onChange={handleFilterChange}
          className="border rounded px-3 py-2"
        >
          <option value="">All Years</option>
          {years.map((y) => (
            <option key={y.id} value={y.id}>{y.value}</option>
          ))}
        </select>

        {categories && categories.length > 0 && (
          <div>
            <select
              name="category_id"
              value={filters.category_id || ''}
              onChange={handleFilterChange}
              className="border rounded px-3 py-2 w-36"
            >
              <option value="">All Categories</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </div>
        )}

        {isExpenses && (
          <select
            name="source"
            value={filters.source || ''}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2 w-40"
          >
            <option value="">All Sources</option>
            {sourceOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        )}
        {!isViewer && (
          <button
            onClick={onAdd}
            className="inline-flex items-center px-3 py-1.5 border border-green-300 bg-green-100 text-green-800 rounded font-medium hover:bg-green-200 transition ml-auto"
          >
            Add {label}
          </button>
        )}
      </div>
    </div>
  );
}