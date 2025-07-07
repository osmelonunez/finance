export default function TotalDisplay({
  items = [],
  label = 'Total',
  field,
  currency = '€',
  bgColor = 'bg-green-100',
  borderColor = 'border-green-300',
  textColor = 'text-green-800',
}) {
  if (!field) {
    console.warn('TotalDisplay: No se ha pasado el campo a sumar (field)');
    return null;
  }

  const total = items.reduce((acc, item) => acc + (parseFloat(item[field]) || 0), 0);

  return (
    <div
      className={`${bgColor} border ${borderColor} rounded-lg font-semibold ${textColor} w-full flex items-center justify-end h-10 px-4`}
    >
      <span className="text-base">
        Total: {total.toLocaleString('es-ES', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        })} {currency}
      </span>
    </div>
  );
}
