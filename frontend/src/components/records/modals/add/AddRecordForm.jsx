export default function AddRecordForm({
  newRecord,
  setNewRecord,
  onCancel,
  onSubmit,
  months,
  years,
  categories,
  hasCategory,
  field,
  title,
  type, // <-- recibe el type
}) {
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewRecord((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  // Singulariza el título para mostrar "Add expense:", "Add income:", etc.
  let mainTitle = title || type || "Item";
  if (mainTitle.endsWith('s')) mainTitle = mainTitle.slice(0, -1);
  mainTitle = `${mainTitle.charAt(0).toUpperCase() + mainTitle.slice(1).toLowerCase()}`;

  return (
    <form
      onSubmit={e => { e.preventDefault(); onSubmit(); }}
      className="space-y-4"
    >
      <h2 className="text-xl font-semibold mb-4">Add {mainTitle}</h2>
      <div>
        <label className="font-semibold">
          Name
        </label>
        <input
          className="border rounded px-2 py-1 ml-2"
          name="name"
          value={newRecord.name || ""}
          onChange={handleInputChange}
          required
        />
      </div>
      <div>
        <label className="font-semibold">
          {field.charAt(0).toUpperCase() + field.slice(1)}:
        </label>
        <input
          className="border rounded px-2 py-1 ml-2"
          name={field}
          type="number"
          value={newRecord[field] || ""}
          onChange={handleInputChange}
          required
        />
      </div>
      <div>
        <label className="font-semibold">Month:</label>
        <select
          className="border rounded px-2 py-1 ml-2"
          name="month_id"
          value={newRecord.month_id || ""}
          onChange={handleInputChange}
          required
        >
          <option value="">Select Month</option>
          {months.map((m) => (
            <option key={m.id} value={m.id}>{m.name}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="font-semibold">Year:</label>
        <select
          className="border rounded px-2 py-1 ml-2"
          name="year_id"
          value={newRecord.year_id || ""}
          onChange={handleInputChange}
          required
        >
          <option value="">Select Year</option>
          {years.map((y) => (
            <option key={y.id} value={y.id}>{y.value}</option>
          ))}
        </select>
      </div>
      {hasCategory && (
        <div>
          <label className="font-semibold">Category:</label>
          <select
            className="border rounded px-2 py-1 ml-2"
            name="category_id"
            value={newRecord.category_id || ""}
            onChange={handleInputChange}
            required
          >
            <option value="">Select Category</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
        </div>
      )}
      {/* Solo para expenses */}
      {type === "expenses" && (
        <div>
          <label className="font-semibold">Source:</label>
          <select
            className="border rounded px-2 py-1 ml-2"
            name="source"
            value={newRecord.source || "current_month"}
            onChange={handleInputChange}
            required
          >
            <option value="current_month">Current month</option>
            <option value="general_savings">General savings</option>
          </select>
        </div>
      )}
      <div className="flex justify-end gap-3 mt-4">
        <button
          type="button"
          className="bg-gray-300 hover:bg-gray-400 text-gray-800 rounded px-4 py-2"
          onClick={onCancel}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="bg-green-600 hover:bg-green-700 text-white rounded px-4 py-2"
        >
          Add
        </button>
      </div>
    </form>
  );
}
