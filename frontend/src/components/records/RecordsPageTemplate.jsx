import { useState, useEffect } from 'react';
import useRecordsData from '../../hooks/useRecordsData';
import useFilteredRecords from '../../hooks/useFilteredRecords';
import useCategoriesData from '../../hooks/useCategoriesData';
import useAuthToken from '../../hooks/useAuthToken';
import FiltersBar from './FiltersBarRecords';
import RecordTable from './RecordTable';
import CopyRecordModal from './CopyRecordModal';
import TotalDisplay from '../common/TotalDisplay';
import Pagination from '../common/Pagination';
import Notification from '../common/Notification';
import AddRecordModal from './AddRecordModal';
import EditRecordModal from './EditRecordModal';
import DeleteModal from './DeleteModal';
import { isValidRecord } from '../utils/validation';
import { showNotification } from '../utils/showNotification';
import { addRecord, updateRecord, deleteRecord } from '../utils/records';

export default function RecordsPageTemplate({
  type,
  title,
  endpoint,
  field,
  color,
  storageKey,
  hasCategory = false
}) {
  const token = useAuthToken();
  const isExpenses = type === 'expenses';
  const { categories } = useCategoriesData();

  const {
    records,
    setRecords,
    months,
    years,
    loading,
  } = useRecordsData(endpoint);

  const [filters, setFilters] = useState({ month_id: '', year_id: '', category_id: '' });
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    setCurrentPage(1);
  }, [sort]);

  const [newRecord, setNewRecord] = useState({
    name: '',
    [field]: '',
    month_id: '',
    year_id: '',
    ...(isExpenses && { category_id: '' }),
  });

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

  const handleAdd = async () => {
    console.log('🚀 Trying to add record:', newRecord);

    const requiredFields = ['name', field, 'month_id', 'year_id'];
    if (requiredFields.some(key => !newRecord[key] || newRecord[key].toString().trim() === '')) {
      console.warn('❌ Missing required fields:', newRecord);
      setError('All fields are required.');
      return;
    }

    try {
      const success = await addRecord(endpoint, newRecord, setRecords, setNotification, token);
      console.log('✅ Submission result:', success);

      if (success) {
        setNewRecord({ name: '', [field]: '', month_id: '', year_id: '', ...(isExpenses && { category_id: '' }) });
        setShowAddModal(false);
        setError('');
      } else {
        console.error('❌ addRecord returned false.');
        setError('Failed to add record.');
      }
    } catch (err) {
      console.error('🔥 Error while submitting record:', err);
      setError('Unexpected error during submission.');
    }
  };

  const handleCopyConfirm = async () => {
    const { record, targetMonth, targetYear } = copyState;

    if (!record || !targetMonth || !targetYear) {
      showNotification(setNotification, {
        type: 'error',
        message: 'Please select both month and year.',
      });
      return;
    }

    const newEntry = {
      name: record.name,
      [field]: record[field],
      month_id: targetMonth,
      year_id: targetYear,
      ...(isExpenses && { category_id: record.category_id }),
    };

    try {
      const success = await addRecord(endpoint, newEntry, setRecords, setNotification, token, `${title.replace(/s$/, '')} copied successfully!`);
      console.log('📋 Copy result:', success);

      if (success) {
        setCopyState({ show: false, record: null, targetMonth: '', targetYear: '' });
      }
    } catch (err) {
      console.error('🔥 Error copying record:', err);
      setNotification({
        type: 'error',
        message: `Unexpected error while copying ${title.toLowerCase()}.`,
      });
    }
  };

  const handleDelete = async () => {
    try {
      const success = await deleteRecord(endpoint, recordToDelete.id, setRecords, setNotification, token);
      console.log('🗑️ Delete result:', success);

      if (success) {
        setShowDeleteModal(false);
        setRecordToDelete(null);
      } else {
        setNotification({ type: 'error', message: 'Failed to delete record.' });
      }
    } catch (err) {
      console.error('🔥 Error while deleting record:', err);
      setNotification({ type: 'error', message: 'Unexpected error while deleting record.' });
    }
  };

  const handleEdit = async () => {
    if (!isValidRecord(editingRecord, field)) {
      setError('Please fill out all fields');
      return;
    }

    try {
      const success = await updateRecord(endpoint, editingRecord, setRecords, setNotification, token);
      console.log('✅ Update result:', success);

      if (success) {
        setShowEditModal(false);
        setEditingRecord(null);
        setError('');
      } else {
        setError('Failed to update record.');
      }
    } catch (err) {
      console.error('🔥 Error while updating record:', err);
      setError('Unexpected error during update.');
    }
  };

  return (
    <div className="records-page">
      <h2 className={`text-2xl font-semibold mb-4 text-center text-${color}`}>{title}</h2>

      <FiltersBar
        filters={filters}
        setFilters={setFilters}
        months={months}
        years={years}
        categories={hasCategory ? categories : null}
        search={search}
        setSearch={setSearch}
        sort={sort}
        setSort={setSort}
        onAdd={() => setShowAddModal(true)} 
      />

      <div className="my-4">
        <TotalDisplay items={filtered} field={field} />
      </div>

      <RecordTable
        records={paginated}
        field={field}
        color={color}
        hasCategory={hasCategory}
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
        totalPages={Math.ceil(filtered.length / itemsPerPage)}
        onPageChange={setCurrentPage}
      />

      {showAddModal && (
        <AddRecordModal
          type={type}
          categories={categories}
          isOpen={showAddModal}
          onCancel={() => setShowAddModal(false)}
          onConfirm={handleAdd}
          record={newRecord}
          onChange={(e) =>
            setNewRecord({ ...newRecord, [e.target.name]: e.target.value })
          }
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
          onChange={(e) =>
            setEditingRecord({ ...editingRecord, [e.target.name]: e.target.value })
          }
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
          type={type}
          categories={categories}
          isOpen={copyState.show}
          onCancel={() =>
            setCopyState((prev) => ({ ...prev, show: false }))
          }
          onConfirm={handleCopyConfirm}
          record={copyState.record}
          months={months}
          years={years}
          targetMonth={copyState.targetMonth}
          setTargetMonth={(value) =>
            setCopyState((prev) => ({ ...prev, targetMonth: value }))
          }
          targetYear={copyState.targetYear}
          setTargetYear={(value) =>
            setCopyState((prev) => ({ ...prev, targetYear: value }))
          }
          label={title.replace(/s$/, '')}
          hasCategory={hasCategory}
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
