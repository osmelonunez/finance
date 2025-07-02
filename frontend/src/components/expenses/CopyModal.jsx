import Modal from '../common/Modal';

export default function CopyModal({
  isOpen,
  onCancel,
  onConfirm,
  expense,
  months,
  years,
  targetMonth,
  setTargetMonth,
  targetYear,
  setTargetYear,
}) {
  return (
    <Modal
      title="Copy Expense"
      isOpen={isOpen}
      onCancel={onCancel}
      onConfirm={onConfirm}
    >
      <p className="text-gray-700">
        You're copying: <strong>{expense?.name}</strong>
      </p>

      <div className="grid grid-cols-2 gap-4 mt-4">
        <select
          value={targetMonth}
          onChange={(e) => setTargetMonth(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="">Select Month</option>
          {months.map((m) => (
            <option key={m.id} value={m.id}>
              {m.name}
            </option>
          ))}
        </select>

        <select
          value={targetYear}
          onChange={(e) => setTargetYear(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="">Select Year</option>
          {years.map((y) => (
            <option key={y.id} value={y.id}>
              {y.value}
            </option>
          ))}
        </select>
      </div>
    </Modal>
  );
}
