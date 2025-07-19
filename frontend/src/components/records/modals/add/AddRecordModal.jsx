import ModalOverlay from "./ModalOverlay";
import AddRecordForm from "./AddRecordForm";
import { useEffect } from "react";

export default function AddRecordModal(props) {
  // Set default source if not set
  useEffect(() => {
    if (!props.newRecord.source) {
      props.setNewRecord((prev) => ({
        ...prev,
        source: "current_month"
      }));
    }
  }, [props.newRecord.source, props.setNewRecord]);

  return (
    <ModalOverlay isOpen={props.isOpen} onClose={props.onClose}>
      <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl p-6 space-y-6 relative">
        <AddRecordForm
          {...props}
          onCancel={props.onClose}
          onSubmit={props.onConfirm}
        />
      </div>
    </ModalOverlay>
  );
}
