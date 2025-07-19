import { useState } from "react";

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
  type,
}) {
  const [multiAdd, setMultiAdd] = useState(false);
  const [selectedYears, setSelectedYears] = useState([]);
  const [selectedMonths, setSelectedMonths] = useState([]);

  let mainTitle = title || type || "Item";
  if (mainTitle.endsWith('s')) mainTitle = mainTitle.slice(0, -1);
  mainTitle = `${mainTitle.charAt(0).toUpperCase() + mainTitle.slice(1).toLowerCase()}`;

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewRecord((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  // Preview: combina todos los meses/años seleccionados
  const recordsPreview =
    selectedYears.length > 0 && selectedMonths.length > 0
      ? selectedYears.flatMap(yearId =>
          selectedMonths.map(monthId => {
            const y = years.find(y => Number(y.id) === Number(yearId));
            const m = months.find(m => Number(m.id) === Number(monthId));
            return {
              year_id: y?.id,
              year_value: y?.value,
              month_id: m?.id,
              month_name: m?.name,
              key: `${yearId}-${monthId}`,
            };
          })
        )
      : [];

  return (
    <form
      onSubmit={e => {
        e.preventDefault();
        if (multiAdd) {
          onSubmit({
            multiAdd: true,
            selectedYears,
            selectedMonths,
          });
        } else {
          onSubmit({ multiAdd: false });
        }
      }}
      className="space-y-4"
    >
      <h2 className="text-xl font-semibold mb-4">Add {mainTitle}</h2>

      <div className="flex items-center gap-3 mb-2">
        <input
          type="checkbox"
          id="multiAdd"
          checked={multiAdd}
          onChange={e => {
            setMultiAdd(e.target.checked);
            setSelectedYears([]);
            setSelectedMonths([]);
          }}
        />
        <label htmlFor="multiAdd" className="text-sm font-medium">
          Add in multiple months/years
        </label>
      </div>

      <div>
        <label className="font-semibold">Name</label>
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

      {!multiAdd && (
        <>
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
        </>
      )}

      {/* MultiAdd: Selección de años y meses */}
      {multiAdd && (
        <>
          <div>
            <div className="font-semibold">Years:</div>
            <div className="flex flex-wrap gap-2">
              {years.map(y => (
                <button
                  type="button"
                  key={y.id}
                  className={`px-3 py-1 rounded border ${
                    selectedYears.includes(Number(y.id))
                      ? "bg-teal-500 text-white"
                      : "bg-gray-100 text-gray-800 hover:bg-gray-200"
                  }`}
                  onClick={() =>
                    setSelectedYears(prev =>
                      prev.includes(Number(y.id))
                        ? prev.filter(id => id !== Number(y.id))
                        : [...prev, Number(y.id)]
                    )
                  }
                >
                  {y.value}
                </button>
              ))}
            </div>
          </div>
          <div>
            <div className="font-semibold mt-2">Months:</div>
            <div className="flex flex-wrap gap-2">
              {months.map(m => (
                <button
                  type="button"
                  key={m.id}
                  className={`px-3 py-1 rounded border ${
                    selectedMonths.includes(Number(m.id))
                      ? "bg-teal-500 text-white"
                      : "bg-gray-100 text-gray-800 hover:bg-gray-200"
                  }`}
                  onClick={() =>
                    setSelectedMonths(prev =>
                      prev.includes(Number(m.id))
                        ? prev.filter(id => id !== Number(m.id))
                        : [...prev, Number(m.id)]
                    )
                  }
                >
                  {m.name}
                </button>
              ))}
            </div>
          </div>
          {/* Preview */}
          <div className="bg-gray-100 border border-gray-300 rounded p-4 my-3">
            <div className="font-semibold mb-2">Records to be created:</div>
            <div className="max-h-24 overflow-y-auto border border-gray-200 rounded" style={{ minHeight: '2.5rem' }}>
              {recordsPreview.length === 0 ? (
                <div className="text-gray-400 italic text-sm px-2 py-1">
                  Select at least one year and one month
                </div>
              ) : (
                <ul className="list-disc ml-6 text-sm">
                  {recordsPreview.map((r, idx) => (
                    <li key={r.key}>
                      Year: {r.year_value}, Month: {r.month_name}
                    </li>
                  ))}
                </ul>
              )}
            </div>
            {recordsPreview.length > 5 && (
              <div className="text-xs text-gray-500 mt-1">
                Scroll to see more ({recordsPreview.length} total)
              </div>
            )}
          </div>
        </>
      )}

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
          disabled={
            (multiAdd && (selectedYears.length === 0 || selectedMonths.length === 0))
          }
        >
          Add
        </button>
      </div>
    </form>
  );
}
