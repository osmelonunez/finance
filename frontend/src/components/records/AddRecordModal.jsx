import Modal from '../common/Modal';
import ErrorMessage from '../common/ErrorMessage';

export default function AddRecordModal({
  isOpen,
  onCancel,
  onConfirm,
  record,
  onChange,
  months,
  years,
  error,
  field,
  type,
  categories = []
}) {
  const isExpenses = type === 'expenses';

  if (!record) return null;

  return (
    <Modal 
      title={`Add ${type.charAt(0).toUpperCase() + type.slice(1).replace(/s$/, '')}`}
      isOpen={isOpen} 
      onCancel={onCancel} 
      onConfirm={onConfirm}>
      {error && <ErrorMessage message={error} />}
      <div className="grid md:grid-cols-4 gap-4 mt-2">
        <input
          name="name"
          value={record.name}
          onChange={onChange}
          placeholder="Name"
          className="border rounded px-3 py-2"
        />

        <input
          name={field}
          value={record[field]}
          onChange={onChange}
          placeholder={isExpenses ? "Cost" : field.charAt(0).toUpperCase() + field.slice(1)}
          type="number"
          className="border rounded px-3 py-2"
        />

        <select
          name="month_id"
          value={record.month_id}
          onChange={onChange}
          className="border rounded px-3 py-2"
        >
          <option value="">Month</option>
          {months.map((m) => (
            <option key={m.id} value={m.id}>{m.name}</option>
          ))}
        </select>

        <select
          name="year_id"
          value={record.year_id}
          onChange={onChange}
          className="border rounded px-3 py-2"
        >
          <option value="">Year</option>
          {years.map((y) => (
            <option key={y.id} value={y.id}>{y.value}</option>
          ))}
        </select>

        {isExpenses && (
          <select
            name="category_id"
            value={record.category_id || ''}
            onChange={onChange}
            className="border rounded px-3 py-2 col-span-2"
          >
            <option value="">Select Category</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
        )}

        {isExpenses && (
          <select
            name="source"
            value={record.source || 'current_month'}
            onChange={onChange}
            className="border rounded px-3 py-2 col-span-2"
          >
            <option value="current_month">Current month</option>
            <option value="general_savings">General savings</option>
          </select>
        )}

      </div>
    </Modal>
  );
}
