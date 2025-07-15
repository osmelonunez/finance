export default function SimpleModal({ isOpen, onClose, title, children }) {
  if (!isOpen) return null;

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      onClick={handleOverlayClick}
      tabIndex={-1}
      role="dialog"
      aria-modal="true"
    >
      <div
        className="bg-white rounded-lg shadow-lg w-full max-w-2xl p-6 space-y-6 relative"
        onClick={e => e.stopPropagation()}
      >
        <h2 className="text-xl font-semibold mb-4">{title}</h2>
        {/* Solo los children, no botones aquí */}
        <div>{children}</div>
      </div>
    </div>
  );
}
