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
  categories = []
}) {
  const isExpenses = type === 'expenses';

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

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
          <option value="amount">Amount</option>
          <option value="month">Month</option>
          <option value="year">Year</option>
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

        <button
          onClick={onAdd}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 ml-auto"
        >
          Add {label}
        </button>
      </div>

      {isExpenses && categories.length > 0 && (
        <div>
          <label className="block text-sm font-medium">Categoría</label>
          <select
            name="category_id"
            value={filters.category_id || ''}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2"
          >
            <option value="">All</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
}