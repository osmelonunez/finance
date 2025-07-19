import AddRecordModal from './modals/add/AddRecordModal';
import AlertModal from './modals/alert/AlertModal';

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
  title,

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
          onClose={() => setShowAddModal(false)}
          onConfirm={() => handleAdd(newRecord)}
          record={newRecord}
          onChange={e => setNewRecord({ ...newRecord, [e.target.name]: e.target.value })}
          months={months}
          years={years}
          error={error}
          field={field}
          hasCategory={hasCategory}
          newRecord={newRecord}
          setNewRecord={setNewRecord}
          title={title}
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
