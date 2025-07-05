import { useState } from 'react';
import useRecordsData from '../../hooks/useRecordsData';
import useFilteredRecords from '../../hooks/useFilteredRecords';
import FiltersBar from './FiltersBarRecords';
import RecordTable from './RecordTable';
import CopyRecordModal from './CopyRecordModal';
import TotalDisplay from '../common/TotalDisplay';
import Pagination from '../common/Pagination';
import Notification from '../common/Notification';
import AddRecordModal from './AddRecordModal';
import EditRecordModal from './EditRecordModal';
import DeleteModal from '../expenses/DeleteModal';
import { addRecord, updateRecord, deleteRecord } from '../utils/records';
import { isValidRecord } from '../utils/validation';
import { showNotification } from '../utils/showNotification';

export default function RecordsPageTemplate({
  title,
  endpoint,
  field,
  color,
  storageKey,
  hasCategory = false
}) {
  const {
    records,
    setRecords,
    months,
    years,
    loading,
  } = useRecordsData(endpoint);

  const [filters, setFilters] = useState({ month_id: '', year_id: '' });
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [notification, setNotification] = useState(null);

  const [newRecord, setNewRecord] = useState({ name: '', [field]: '', month_id: '', year_id: '' });
  const [editingRecord, setEditingRecord] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [recordToDelete, setRecordToDelete] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [copyState, setCopyState] = useState({ show: false, record: null, targetMonth: '', targetYear: '' });
  const [error, setError] = useState('');

  const filtered = useFilteredRecords(records, filters, search, sort, field);
  const itemsPerPage = 10;
  const paginated = filtered.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handleCopyConfirm = async () => {
    const { record, targetMonth, targetYear } = copyState;

    if (!record || !targetMonth || !targetYear) {
      //showNotification(setNotification, { type: 'error', message: 'Please select month and year.' });
      showNotification(setNotification, { type: 'error', message: 'Please select month and year.' });
      return;
    }

    const newEntry = {
      name: record.name,
      [field]: record[field],
      month_id: targetMonth,
      year_id: targetYear
    };

    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newEntry),
    });

    if (res.ok) {
      const updated = await res.json();
      setRecords(updated);
      showNotification(setNotification, { type: 'success', message: `${title.replace(/s$/, '')} copied successfully!` });
      setCopyState({ show: false, expense: null, targetMonth: '', targetYear: '' });
    } else {
      setNotification({ type: 'error', message: `Failed to copy ${title.toLowerCase()}.` });
    }
  };

  const handleAdd = async () => {
    if (!isValidRecord(newRecord, field)) {
      setError('Please fill out all fields');
      return;
    }
    const success = await addRecord(endpoint, newRecord, setRecords, setNotification);
    if (success) {
      setNewRecord({ name: '', [field]: '', month_id: '', year_id: '' });
      setShowAddModal(false);
      setError('');
    }
  };

  const handleEdit = async () => {
    if (!isValidRecord(editingRecord, field)) return;
    const success = await updateRecord(endpoint, editingRecord, setRecords, setNotification);
    if (success) {
      setShowEditModal(false);
      setEditingRecord(null);
    }
  };

  const handleDelete = async () => {
    const success = await deleteRecord(endpoint, recordToDelete.id, setRecords, setNotification);
    if (success) {
      setShowDeleteModal(false);
      setRecordToDelete(null);
    }
  };

  const handleCopy = async () => {
    const { targetMonth, targetYear, record } = copyState;
    if (!targetMonth || !targetYear) return;

    const newEntry = {
      name: record.name,
      [field]: record[field],
      month_id: targetMonth,
      year_id: targetYear,
    };

    const success = await addRecord(endpoint, newEntry, setRecords, setNotification, `${title} copied successfully!`);
    if (success) {
      setCopyState({ show: false, record: null, targetMonth: '', targetYear: '' });
    }
  };

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">{title}</h1>
      <FiltersBar
        filters={filters}
        setFilters={setFilters}
        search={search}
        setSearch={setSearch}
        sort={sort}
        setSort={setSort}
        onAdd={() => setShowAddModal(true)}
        hasCategory={hasCategory}
        months={months}
        years={years}
      />

      <TotalDisplay
        items={filtered}
        label={`Total ${title.toLowerCase()}`}
        field={field}
        bgColor={`bg-${color}-100`}
        borderColor={`border-${color}-300`}
        textColor={`text-${color}-800`}
      />

      <RecordTable
        records={paginated}
        field={field}
        onEdit={(record) => {
          setEditingRecord({ ...record });
          setShowEditModal(true);
        }}
        onDelete={(record) => {
          setRecordToDelete(record);
          setShowDeleteModal(true);
        }}
        onCopy={(record) => {
          setCopyState({ show: true, record, targetMonth: '', targetYear: '' });
        }}
      />

      <Pagination
        currentPage={currentPage}
        totalItems={filtered.length}
        itemsPerPage={itemsPerPage}
        onPageChange={setCurrentPage}
      />

      {showAddModal && (
        <AddRecordModal
          isOpen={showAddModal}
          onCancel={() => setShowAddModal(false)}
          onConfirm={handleAdd}
          record={newRecord}
          onChange={(e) => setNewRecord({ ...newRecord, [e.target.name]: e.target.value })}
          months={months}
          years={years}
          error={error}
          field={field}
        />
      )}

      {showEditModal && (
        <EditRecordModal
          isOpen={showEditModal}
          onCancel={() => setShowEditModal(false)}
          onConfirm={handleEdit}
          record={editingRecord}
          onChange={(e) => setEditingRecord({ ...editingRecord, [e.target.name]: e.target.value })}
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

      {copyState.show && (
      <CopyRecordModal
        isOpen={copyState.show}
        onCancel={() => setCopyState(prev => ({ ...prev, show: false }))}
        onConfirm={handleCopyConfirm}
        record={copyState.record}
        months={months}
        years={years}
        targetMonth={copyState.targetMonth}
        setTargetMonth={(value) => setCopyState(prev => ({ ...prev, targetMonth: value }))}
        targetYear={copyState.targetYear}
        setTargetYear={(value) => setCopyState(prev => ({ ...prev, targetYear: value }))}
        label={title.replace(/s$/, '')}
      />

      )}

      {notification && (
        <Notification
          type={notification.type}
          message={notification.message}
          onClose={() => setNotification(null)}
        />
      )}

    </div>
  );
}
