import { useEffect } from "react";

export default function ModalOverlay({ isOpen, onClose, children }) {
  useEffect(() => {
    if (!isOpen) return;
    const handleEsc = (e) => {
      if (e.key === "Escape" && typeof onClose === "function") {
        onClose();
      }
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      onClick={e => { if (e.target === e.currentTarget && typeof onClose === "function") onClose(); }}
      tabIndex={-1}
      role="dialog"
      aria-modal="true"
    >
      {children}
    </div>
  );
}
