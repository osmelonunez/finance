import AddRecordModal from './AddRecordModal';
import EditRecordModal from './EditRecordModal';
import DeleteModal from './DeleteModal';
import CopyRecordModal from './CopyRecordModal';
import InfoModal from './InfoModal';

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

  showEditModal,
  setShowEditModal,
  handleEdit,
  editingRecord,
  setEditingRecord,

  showDeleteModal,
  setShowDeleteModal,
  handleDelete,

  copyState,
  setCopyState,
  handleCopyConfirm,
  title,

  infoRecord,
  setInfoRecord
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

      {showEditModal && (
        <EditRecordModal
          type={type}
          categories={categories}
          isOpen={showEditModal}
          onCancel={() => setShowEditModal(false)}
          onConfirm={handleEdit}
          record={editingRecord}
          onChange={e => setEditingRecord({ ...editingRecord, [e.target.name]: e.target.value })}
          months={months}
          years={years}
          field={field}
        />
      )}

      {showDeleteModal && (
        <DeleteModal
          isOpen={showDeleteModal}
          onCancel={() => setShowDeleteModal(false)}
          onConfirm={handleDelete}
        />
      )}

      {copyState?.show && (
        <CopyRecordModal
          type={type}
          categories={categories}
          isOpen={copyState.show}
          onCancel={() => setCopyState(prev => ({ ...prev, show: false }))}
          onConfirm={handleCopyConfirm}
          record={copyState.record}
          months={months}
          years={years}
          targetMonth={copyState.targetMonth}
          setTargetMonth={value => setCopyState(prev => ({ ...prev, targetMonth: value }))}
          targetYear={copyState.targetYear}
          setTargetYear={value => setCopyState(prev => ({ ...prev, targetYear: value }))}
          label={title.replace(/s$/, '')}
          hasCategory={hasCategory}
        />
      )}

      {infoRecord && (
        <InfoModal
          record={infoRecord}
          onClose={() => setInfoRecord(null)}
        />
      )}

    </>
  );
}
