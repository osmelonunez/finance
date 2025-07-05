export default function Modal({ isOpen, onCancel, onConfirm, title, children }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl p-6 space-y-6">
        <h2 className="text-xl font-semibold">{title}</h2>
        <div>{children}</div>
        <div className="flex justify-end space-x-4 mt-6">
          <button
            type="button"
            onClick={onCancel}
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={() => {
              console.log('✅ Botón confirmar PRESIONADO');
              onConfirm();
            }}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
          >
            Confirmar
          </button>
        </div>
      </div>
    </div>
  );
}