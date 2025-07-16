import { useState } from "react";

export default function RecurrenceSelector({
  record,
  years = [],
  months = [],
  onSave,
  onCancel
}) {
  const [type, setType] = useState(""); // 'years' or 'months'
  const [selected, setSelected] = useState([]);

  // Get future years from record year (as before)
  const recordYear = Number(record?.year_value) || new Date().getFullYear();
  const futureYears = years.filter(y => Number(y.value) >= recordYear);

  // Render options as toggle buttons, using name for months and value for years
  const renderOptions = (options) => (
    <div className="flex gap-3 flex-wrap mt-2">
      {options.map(opt => (
        <button
          key={opt.id}
          type="button"
          className={`px-3 py-1 rounded border ${
            selected.includes(opt.id)
              ? 'bg-teal-500 text-white'
              : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
          }`}
          onClick={() => {
            setSelected(prev =>
              prev.includes(opt.id)
                ? prev.filter(val => val !== opt.id)
                : [...prev, opt.id]
            );
          }}
        >
          {type === "years" ? opt.value : opt.name}
        </button>
      ))}
    </div>
  );

  return (
    <div className="flex flex-col gap-5">
      {/* Radio buttons for recurrence type */}
      <div className="flex gap-6 justify-center">
        <label className="flex items-center cursor-pointer gap-2">
          <input
            type="radio"
            name="recurrencyType"
            checked={type === 'years'}
            onChange={() => { setType('years'); setSelected([]); }}
            className="accent-teal-500"
          />
          <span className="font-semibold">Currency years</span>
        </label>
        <label className="flex items-center cursor-pointer gap-2">
          <input
            type="radio"
            name="recurrencyType"
            checked={type === 'months'}
            onChange={() => { setType('months'); setSelected([]); }}
            className="accent-teal-500"
          />
          <span className="font-semibold">Currency months</span>
        </label>
      </div>

      {/* Show only years >= record year if years is selected, else months */}
      <div>
        {type === "years"
          ? renderOptions(futureYears)
          : type === "months"
            ? renderOptions(months)
            : null}
      </div>

      {/* Preview the records to be created */}
      {type && selected.length > 0 && (
        <div className="bg-gray-100 border border-gray-300 rounded p-4 mb-3">
          <div className="font-semibold mb-2">Records to be created:</div>
            <ul className="list-disc ml-6 text-sm">
              {type === 'years' && selected.length > 0 && selected.map(sel =>
                months.map(m => (
                  <li key={`${sel}-${m.id}`}>
                    {`Year: ${years.find(y => y.id === sel)?.value || sel}, Month: ${m.name}`}
                  </li>
                ))
              )}
              {type === 'months' && selected.length > 0 && selected.map(sel => (
                <li key={sel}>
                  {`Month: ${months.find(m => m.id === sel)?.name || sel}, Year: ${years.find(y => y.id === record?.year_id)?.value || record?.year_id}`}
                </li>
              ))}
            </ul>
        </div>
      )}

      <div className="flex justify-end gap-3 mt-2">
        <button
          onClick={onCancel}
          className="bg-gray-300 hover:bg-gray-400 text-gray-800 rounded px-4 py-2"
        >
          Cancel
        </button>
        <button
          onClick={() => onSave({ type, selected })}
          className="bg-teal-500 hover:bg-teal-600 text-white rounded px-4 py-2"
          disabled={!type || selected.length === 0}
        >
          Save
        </button>
      </div>
    </div>
  );
}
