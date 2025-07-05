import Modal from '../common/Modal';

export default function CopyRecordModal({
  isOpen,
  onCancel,
  onConfirm,
  record,
  months,
  years,
  targetMonth,
  setTargetMonth,
  targetYear,
  setTargetYear,
  label = 'Record',
  type,
  categories = []
}) {
  const isExpenses = type === 'expenses';

  return (
    <Modal isOpen={isOpen} onCancel={onCancel} onConfirm={onConfirm} title={`Copy ${label}`}>
      <div className="space-y-4">
        <p className="text-gray-600">
          You are copying <strong>{record?.name}</strong>.
          Please select the new month and year for the copied {label.toLowerCase()}.
        </p>

        

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <select
            value={targetMonth}
            onChange={(e) => setTargetMonth(e.target.value)}
            className="border rounded px-3 py-2"
          >
            <option value="">Select Month</option>
            {months.map((m) => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>

          <select
            value={targetYear}
            onChange={(e) => setTargetYear(e.target.value)}
            className="border rounded px-3 py-2"
          >
            <option value="">Select Year</option>
            {years.map((y) => (
              <option key={y.id} value={y.id}>{y.value}</option>
            ))}
          </select>
        </div>
      </div>
    </Modal>
  );
}