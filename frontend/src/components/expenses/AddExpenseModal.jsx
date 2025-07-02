import Modal from '../common/Modal';
import ErrorMessage from '../common/ErrorMessage';

export default function AddExpenseModal({
  isOpen,
  onCancel,
  onConfirm,
  expense,
  onChange,
  months,
  years,
  categories,
  error,
}) {
  return (
    <Modal
      title="Add Expense"
      isOpen={isOpen}
      onCancel={onCancel}
      onConfirm={onConfirm}
    >
      {error && <ErrorMessage message={error} />}

      <div className="grid md:grid-cols-4 gap-4 mt-2">
        <input
          name="name"
          value={expense.name}
          onChange={onChange}
          placeholder="Name"
          className="border rounded px-3 py-2"
        />
        <input
          name="cost"
          value={expense.cost}
          onChange={onChange}
          placeholder="Cost"
          type="number"
          className="border rounded px-3 py-2"
        />
        <select
          name="month_id"
          value={expense.month_id}
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
          value={expense.year_id}
          onChange={onChange}
          className="border rounded px-3 py-2"
        >
          <option value="">Year</option>
          {years.map((y) => (
            <option key={y.id} value={y.id}>{y.value}</option>
          ))}
        </select>
        <select
          name="category_id"
          value={expense.category_id}
          onChange={onChange}
          className="border rounded px-3 py-2"
        >
          <option value="">Category</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>{cat.name}</option>
          ))}
        </select>
      </div>
    </Modal>
  );
}
