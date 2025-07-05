export default function TotalDisplay({
  items = [],
  label = 'Total',
  field = 'cost',
  currency = '€',
  bgColor = 'bg-green-100',
  borderColor = 'border-green-300',
  textColor = 'text-green-800',
}) {
  const total = items.reduce((acc, item) => acc + parseFloat(item[field] || 0), 0);

  return (
    <div className={`${bgColor} border ${borderColor} rounded-lg p-4 text-right font-semibold ${textColor}`}>
      {label}: {total.toLocaleString('es-ES', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })} {currency}
    </div>
  );
}
