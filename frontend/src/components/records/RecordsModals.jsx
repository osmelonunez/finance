import AddRecordModal from './AddRecordModal';
import AlertModal from './AlertModal';

export default function RecordsModals({
  showAddModal,
  setShowAddModal,
  handleAdd,
  newRecord,
  setNewRecord,
  months,
  years,
  error,
  field,
  type,
  categories,
  hasCategory,

  alertRecord,
  setAlertRecord
}) {
  return (
    <>
      {showAddModal && (
        <AddRecordModal
          type={type}
          categories={categories}
          isOpen={showAddModal}
          onCancel={() => setShowAddModal(false)}
          onConfirm={handleAdd}
          record={newRecord}
          onChange={e => setNewRecord({ ...newRecord, [e.target.name]: e.target.value })}
          months={months}
          years={years}
          error={error}
          field={field}
          hasCategory={hasCategory}
        />
      )}

      {alertRecord && (
        <AlertModal
          record={alertRecord}
          onClose={() => setAlertRecord(null)}
        />
      )}

    </>
  );
}
