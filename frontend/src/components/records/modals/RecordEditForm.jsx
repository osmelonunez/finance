// RecordEditForm.jsx
export default function RecordEditForm({
  editingRecord,
  setEditingRecord,
  field,
  months,
  years,
  categories,
  hasCategory
}) {
  return (
    <div className="space-y-4">
      <div>
        <label className="font-semibold">Name:</label>
        <input
          className="border rounded px-2 py-1 ml-2"
          name="name"
          value={editingRecord.name}
          onChange={e => setEditingRecord({ ...editingRecord, name: e.target.value })}
        />
      </div>
      <div>
        <label className="font-semibold">{field.charAt(0).toUpperCase() + field.slice(1)}:</label>
        <input
          className="border rounded px-2 py-1 ml-2"
          name={field}
          value={editingRecord[field]}
          onChange={e => setEditingRecord({ ...editingRecord, [field]: e.target.value })}
          type="number"
        />
      </div>
      <div>
        <label className="font-semibold">Month:</label>
        <select
          className="border rounded px-2 py-1 ml-2"
          name="month_id"
          value={editingRecord.month_id}
          onChange={e => setEditingRecord({ ...editingRecord, month_id: e.target.value })}
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
          value={editingRecord.year_id}
          onChange={e => setEditingRecord({ ...editingRecord, year_id: e.target.value })}
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
            value={editingRecord.category_id || ''}
            onChange={e => setEditingRecord({ ...editingRecord, category_id: e.target.value })}
          >
            <option value="">Select Category</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
        </div>
      )}
      {"source" in editingRecord && (
        <div>
          <label className="font-semibold">Source:</label>
          <select
            className="border rounded px-2 py-1 ml-2"
            name="source"
            value={editingRecord.source || ''}
            onChange={e => setEditingRecord({ ...editingRecord, source: e.target.value })}
          >
            <option value="">Select Source</option>
            <option value="current_month">Current month</option>
            <option value="general_savings">General savings</option>
          </select>
        </div>
      )}
    </div>
  );
}
