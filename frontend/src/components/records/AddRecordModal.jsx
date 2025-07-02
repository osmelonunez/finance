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
  field
}) {
  return (
    <Modal title="Add Record" isOpen={isOpen} onCancel={onCancel} onConfirm={onConfirm}>
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
          placeholder={field.charAt(0).toUpperCase() + field.slice(1)}
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
      </div>
    </Modal>
  );
}