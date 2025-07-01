// components/common/Modal.jsx
export default function Modal({ title, children, isOpen, onConfirm, onCancel }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded-xl shadow-xl w-full max-w-md space-y-4">
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        <div>{children}</div>
        <div className="flex justify-end gap-2">
          <button
            onClick={onCancel}
            className="px-4 py-2 border rounded text-gray-600 hover:bg-gray-100"
          >
            Cancelar
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            Confirmar
          </button>
        </div>
      </div>
    </div>
  );
}
