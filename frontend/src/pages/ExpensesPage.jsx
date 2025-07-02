import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FiltersBar from '../components/expenses/FiltersBar';
import ExpensesTable from '../components/expenses/ExpensesTable';
import DeleteModal from '../components/expenses/DeleteModal';
import CopyModal from '../components/expenses/CopyModal';
import AddExpenseModal from '../components/expenses/AddExpenseModal';
import EditExpenseModal from '../components/expenses/EditExpenseModal';
import Notification from '../components/common/Notification';
import ErrorMessage from '../components/common/ErrorMessage';
import TotalDisplay from '../components/common/TotalDisplay';
import Pagination from '../components/common/Pagination';
import useExpensesData from '../hooks/useExpensesData';
import { addExpense, updateExpense, deleteExpense } from '../components/utils/expenses/index';

export default function ExpensesPage() {
  const navigate = useNavigate();
  const [filtered, setFiltered] = useState([]);
  const [filters, setFilters] = useState({ month_id: '', year_id: '', category_id: '' });
  const [newExpense, setNewExpense] = useState({ name: '', cost: '', month_id: '', year_id: '', category_id: '' });
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [expenseToDelete, setExpenseToDelete] = useState(null);
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingExpense, setEditingExpense] = useState(null);
  const [notification, setNotification] = useState({ type: '', message: '' });
  const [error, setError] = useState('');
  const {expenses, setExpenses, categories, months, years, loading} = useExpensesData();


  useEffect(() => {
  if (notification.message) {
    const timer = setTimeout(() => {
      setNotification({ type: '', message: '' });
    }, 2000);

    return () => clearTimeout(timer); // Limpia si el componente cambia antes de tiempo
  }
}, [notification]);

  useEffect(() => {
    let result = [...expenses];
    if (filters.month_id) result = result.filter(e => parseInt(e.month_id) === parseInt(filters.month_id));
    if (filters.year_id) result = result.filter(e => parseInt(e.year_id) === parseInt(filters.year_id));
    if (filters.category_id) result = result.filter(e => e.category_id === parseInt(filters.category_id));
    if (search) result = result.filter(e => e.name.toLowerCase().includes(search.toLowerCase()));
    if (sort === 'name') result.sort((a, b) => a.name.localeCompare(b.name));
    if (sort === 'cost') result.sort((a, b) => parseFloat(b.cost) - parseFloat(a.cost));
    setFiltered(result);
  }, [filters, expenses, search, sort]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewExpense(prev => ({ ...prev, [name]: value }));
  };

    const handleAddExpense = async () => {
      if (
        !newExpense.name ||
        !newExpense.cost ||
        !newExpense.month_id ||
        !newExpense.year_id ||
        !newExpense.category_id
      ) {
        setError('Please fill out all fields');
        return;
      }
    
      const success = await addExpense(newExpense, setExpenses, setNotification);
    
      if (success) {
        setNewExpense({ name: '', cost: '', month_id: '', year_id: '', category_id: '' });
        setShowAddModal(false);
        setError('');
      }
    };

    const handleEditClick = (expense) => {
      setEditingExpense({ ...expense });
      setShowEditModal(true);
    };

    const handleUpdateExpense = async () => {
      if (
        !editingExpense.id ||
        !editingExpense.name ||
        !editingExpense.cost ||
        !editingExpense.month_id ||
        !editingExpense.year_id ||
        !editingExpense.category_id
      ) return;
    
      const success = await updateExpense(editingExpense, setExpenses, setNotification);
    
      if (success) {
        setShowEditModal(false);
        setEditingExpense(null);
      }
    };

  const handleDeleteExpense = (expense) => {
    setExpenseToDelete(expense);
    setShowDeleteModal(true);
  };

    const confirmDeleteExpense = async () => {
      if (!expenseToDelete) return;
    
      const success = await deleteExpense(expenseToDelete.id, setExpenses, setNotification);
    
      if (success) {
        setShowDeleteModal(false);
        setExpenseToDelete(null);
      }
    };

  const [currentPage, setCurrentPage] = useState(1);
  const [copyState, setCopyState] = useState({show: false, expense: null, targetMonth: '',targetYear: ''});
  const itemsPerPage = 10;
  const totalPages = Math.ceil(filtered.length / itemsPerPage);
  const paginated = filtered.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);
  const handleCopyClick = (expense) => {setCopyState({show: true,expense,targetMonth: '',targetYear: ''});};


  if (loading) {
    return <p className="text-center text-gray-500 py-8">Loading data...</p>;
  }

  return (
    <div className="space-y-8">

      {notification.message && (
        <Notification
          type={notification.type}
          message={notification.message}
          onClose={() => setNotification({ type: '', message: '' })}
        />
      )}

      <h2 className="text-2xl font-bold text-gray-800">Expenses</h2>

      <FiltersBar
        filters={filters}
        setFilters={setFilters}
        sort={sort}
        setSort={setSort}
        search={search}
        setSearch={setSearch}
        months={months}
        years={years}
        categories={categories}
        setShowAddModal={setShowAddModal}
      />

      <TotalDisplay
        items={filtered}
        label="Total gastos"
        field="cost"
        bgColor="bg-green-100"
        borderColor="border-green-300"
        textColor="text-green-800"
      />

      <ExpensesTable
        expenses={paginated}
        onEdit={handleEditClick}
        onDelete={handleDeleteExpense}
        onCopy={handleCopyClick}
      />

      <EditExpenseModal
        isOpen={showEditModal}
        onCancel={() => {
          setShowEditModal(false);
          setEditingExpense(null);
        }}
        onConfirm={handleUpdateExpense}
        expense={editingExpense}
        onChange={(e) => {
          const { name, value } = e.target;
          setEditingExpense(prev => ({ ...prev, [name]: value }));
        }}
        months={months}
        years={years}
        categories={categories}
      />

      <AddExpenseModal
        isOpen={showAddModal}
        onCancel={() => setShowAddModal(false)}
        onConfirm={handleAddExpense}
        expense={newExpense}
        onChange={handleInputChange}
        months={months}
        years={years}
        categories={categories}
        error={error}
      />

      <DeleteModal
        isOpen={showDeleteModal}
        onCancel={() => {
          setShowDeleteModal(false);
          setExpenseToDelete(null);
        }}
        onConfirm={confirmDeleteExpense}
        expense={expenseToDelete}
      />

      <CopyModal
        isOpen={copyState.show}
        onCancel={() => setCopyState(prev => ({ ...prev, show: false }))}
        onConfirm={() => {
          const { targetMonth, targetYear, expense } = copyState;
        
          if (!targetMonth || !targetYear) return;
        
          if (
            parseInt(expense.month_id) === parseInt(targetMonth) &&
            parseInt(expense.year_id) === parseInt(targetYear)
          ) {
            setNotification({
              type: 'error',
              message: 'Cannot copy to the same month and year.'
            });
            return;
          }
        
          const newEntry = {
            name: expense.name,
            cost: expense.cost,
            month_id: targetMonth,
            year_id: targetYear,
            category_id: expense.category_id
          };
        
          addExpense(newEntry, setExpenses, setNotification, 'Expense copied successfully!')
            .then(success => {
              if (success) {
                setCopyState({ show: false, expense: null, targetMonth: '', targetYear: '' });
              }
            });
        }}
        expense={copyState.expense}
        months={months}
        years={years}
        targetMonth={copyState.targetMonth}
        setTargetMonth={(value) => setCopyState(prev => ({ ...prev, targetMonth: value }))}
        setTargetYear={(value) => setCopyState(prev => ({ ...prev, targetYear: value }))}
        targetYear={copyState.targetYear}
      />

      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={setCurrentPage}
      />
    </div>
  );
}
