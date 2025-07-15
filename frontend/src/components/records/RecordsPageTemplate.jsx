// 1. React y librerías externas
import { useState, useEffect } from 'react';

// 2. Hooks personalizados
import useAuthToken from '../../hooks/useAuthToken';
import useRecordsData from '../../hooks/records/useRecordsData';
import useFilteredRecords from '../../hooks/records/useFilteredRecords';
import useCategoriesData from '../../hooks/records/useHandleCategoriesData';
import useHandleAdd from '../../hooks/records/useHandleAdd';
import useHandleEdit from '../../hooks/records/useHandleEdit';
import useHandleDelete from '../../hooks/records/useHandleDelete';
import { useAuth } from '../../auth/AuthContext'; // Ajusta la ruta si es diferente


// 3. Componentes locales
import FiltersBar from './FiltersBarRecords';
import RecordTable from './RecordTable';
import RecordsModals from './RecordsModals';
import TotalDisplay from './TotalDisplay';
import Pagination from './Pagination';
import ViewRecordModal from './ViewRecordModal';
import { showNotification } from '../utils/showNotification'; // Importa la función global

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
    fetchData
  } = useRecordsData(endpoint);

  const { user } = useAuth();
  const isViewer = user?.role === 'viewer';

  const [filters, setFilters] = useState({ month_id: '', year_id: '', category_id: '' });
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

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

  const [showAddModal, setShowAddModal] = useState(false);
  const [error, setError] = useState('');
  const [alertRecord, setAlertRecord] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [viewRecord, setViewRecord] = useState(null);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await fetch("/api/alerts", {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
        });
        const data = await res.json();
        setAlerts(Array.isArray(data) ? data : []);
      } catch (err) {
        setAlerts([]);
      }
    };
    fetchAlerts();
  }, []);

  const filtered = useFilteredRecords(records, filters, search, sort, field);
  const itemsPerPage = 10;
  const paginated = filtered.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  // Pasa la función global showNotification a todos los hooks
  const handleAdd = useHandleAdd({ endpoint, field, isExpenses, token, newRecord, setNewRecord, setShowAddModal, setError, setRecords, showNotification, afterSuccess: fetchData });
  const handleDelete = useHandleDelete({ endpoint, setRecords, showNotification, token, afterSuccess: fetchData });
  const handleEdit = useHandleEdit({ endpoint, field, token, setError, setRecords, showNotification, afterSuccess: fetchData });

const handleEditAndRefreshView = async (updatedRecord) => {
  const result = await handleEdit(updatedRecord);
  if (result !== false) {
    setViewRecord(updatedRecord);
  }
  return result;
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
        type={type}
        label={type.charAt(0).toUpperCase() + type.slice(1).replace(/s$/, '')}
        isViewer={isViewer}
      />

      <div className="my-4">
        <TotalDisplay
          items={filtered}
          field={field}
          excludeSource={type === 'expenses' && !filters.source ? 'general_savings' : undefined}
        />
      </div>

      <RecordTable
        records={paginated}
        field={field}
        color={color}
        hasCategory={hasCategory}
        onEdit={setViewRecord}
        isViewer={isViewer}
        onAlert={(record) => {
          console.log('onAlert llamado:', record);
          setAlertRecord(record);
        }}
        recordType={type}
        alerts={alerts}
        onView={setViewRecord}
      />

      <Pagination
        currentPage={currentPage}
        totalPages={Math.ceil(filtered.length / itemsPerPage)}
        onPageChange={setCurrentPage}
      />

      <RecordsModals
        showAddModal={showAddModal}
        setShowAddModal={setShowAddModal}
        handleAdd={handleAdd}
        newRecord={newRecord}
        setNewRecord={setNewRecord}
        months={months}
        years={years}
        error={error}
        field={field}
        type={type}
        categories={categories}
        hasCategory={hasCategory}

        alertRecord={alertRecord}
        setAlertRecord={setAlertRecord}
      />

      {viewRecord && (
        <ViewRecordModal
          isOpen={!!viewRecord}
          onClose={() => setViewRecord(null)}
          record={viewRecord}
          field={field}
          hasCategory={hasCategory}
          title={title}
          months={months}
          years={years}
          categories={categories}
          handleEdit={handleEditAndRefreshView}
          handleDelete={handleDelete}
        />
      )}

    </div>
  );
}
