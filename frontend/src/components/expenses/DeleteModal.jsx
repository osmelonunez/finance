import Modal from '../common/Modal';

export default function DeleteModal({ isOpen, onCancel, onConfirm, expense }) {
  return (
    <Modal
      title="Confirm Delete"
      isOpen={isOpen}
      onCancel={onCancel}
      onConfirm={onConfirm}
    >
      <p className="text-gray-600">
        Are you sure you want to delete <strong>{expense?.name}</strong>?
      </p>
    </Modal>
  );
}
