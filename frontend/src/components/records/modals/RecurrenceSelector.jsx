import { useState } from "react";

export default function RecurrenceSelector({
  record,
  years = [],
  months = [],
  onSave,
  onCancel
}) {
  // State for selected type and options
  const [type, setType] = useState(""); // 'years' or 'months'
  const [selected, setSelected] = useState([]);

  // Use the year from the record as the minimum for future years
    const recordYear = Number(record?.year_value) || new Date().getFullYear();


console.log('Record:', record);              // Ver todo el registro
console.log('Record year:', recordYear);     // El año base que se usará
console.log('All years:', years);            // El array completo de años

    const futureYears = years.filter(y => Number(y.value) >= recordYear);
console.log('Filtered future years:', futureYears); // Los años que realmente se muestran

  // Render the available options (years or months) as toggle buttons
  const renderOptions = (options) => (
    <div className="flex gap-3 flex-wrap mt-2">
      {options.map(opt => (
        <button
          key={opt.id || opt.value}
          type="button"
          className={`px-3 py-1 rounded border ${
            selected.includes(opt.value || opt.id)
              ? 'bg-teal-500 text-white'
              : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
          }`}
          onClick={() => {
            setSelected(prev =>
              prev.includes(opt.value || opt.id)
                ? prev.filter(val => val !== (opt.value || opt.id))
                : [...prev, (opt.value || opt.id)]
            );
          }}
        >
          {opt.name || opt.value}
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
