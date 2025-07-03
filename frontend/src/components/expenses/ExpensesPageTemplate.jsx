import { useState } from 'react';
import FiltersBar from './FiltersBar';
import ExpensesTable from './ExpensesTable';
import AddExpenseModal from './AddExpenseModal';
import EditExpenseModal from './EditExpenseModal';
import CopyModal from './CopyModal';
import DeleteModal from './DeleteModal';
import Notification from '../common/Notification';
import TotalDisplay from '../common/TotalDisplay';
import Pagination from '../common/Pagination';
import useExpensesData from '../../hooks/useExpensesData';
import useFilteredExpenses from '../../hooks/useFilteredExpenses';
import { isValidExpense } from '../utils/validation';
import { addExpense, updateExpense, deleteExpense } from '../utils/expenses';

export default function ExpensesPageTemplate() {
  const {
    expenses,
    setExpenses,
    months,
    years,
    categories,
    loading,
    error
  } = useExpensesData();

  const [filters, setFilters] = useState({ month_id: '', year_id: '', category_id: '' });
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('');
  const [notification, setNotification] = useState(null);

  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const [newExpense, setNewExpense] = useState({ name: '', cost: '', month_id: '', year_id: '', category_id: '' });
  const [editingExpense, setEditingExpense] = useState(null);
  const [expenseToDelete, setExpenseToDelete] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [copyState, setCopyState] = useState({ show: false, expense: null, targetMonth: '', targetYear: '' });

  const filtered = useFilteredExpenses(expenses, filters, search, sort);
  const totalPages = Math.ceil(filtered.length / itemsPerPage);
  const paginated = filtered.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handleAdd = async () => {
    if (!isValidExpense(newExpense)) {
      setNotification({ type: 'error', message: 'Please fill out all fields.' });
      return;
    }
    await addExpense(newExpense, setExpenses, setNotification);
    setShowAddModal(false);
    setNewExpense({ name: '', cost: '', month_id: '', year_id: '', category_id: '' });
  };

  const handleUpdate = async () => {
    if (!isValidExpense(editingExpense)) {
      setNotification({ type: 'error', message: 'Please fill out all fields.' });
      return;
    }
    await updateExpense(editingExpense, setExpenses, setNotification);
    setShowEditModal(false);
    setEditingExpense(null);
  };

  const handleDelete = async () => {
    console.log('Borrando gasto:', expenseToDelete);
    await deleteExpense(expenseToDelete.id, setExpenses, setNotification);
    setShowDeleteModal(false);
    setExpenseToDelete(null);
  };

  const handleCopy = async () => {
    const { expense, targetMonth, targetYear } = copyState;
    if (!expense || !targetMonth || !targetYear) return;
    const copy = {
      name: expense.name,
      cost: expense.cost,
      month_id: targetMonth,
      year_id: targetYear,
      category_id: expense.category_id
    };
    await addExpense(copy, setExpenses, setNotification);
    setCopyState({ show: false, expense: null, targetMonth: '', targetYear: '' });
  };

  if (loading) return <p className="text-center text-gray-500 py-8">Loading expenses...</p>;
  if (error) return <p className="text-center text-red-500 py-8">{error}</p>;

  return (
    <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-800">Expenses</h1>
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
        hasCategory={true}
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
        onEdit={(e) => {
          setEditingExpense(e);
          setShowEditModal(true);
        }}
        onDelete={(e) => {
          setExpenseToDelete(e);
          setShowDeleteModal(true);
        }}
        onCopy={(e) => {
          setCopyState({ show: true, expense: e, targetMonth: '', targetYear: '' });
        }}
      />

      <Pagination
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        totalPages={totalPages}
      />

      {notification && <Notification {...notification} onClose={() => setNotification(null)} />}

      <AddExpenseModal
        isOpen={showAddModal}
        onCancel={() => setShowAddModal(false)}
        onConfirm={handleAdd}
        expense={newExpense}
        setExpense={setNewExpense}
        months={months}
        years={years}
        categories={categories}
      />

    <EditExpenseModal
      isOpen={showEditModal}
      onCancel={() => setShowEditModal(false)}
      onConfirm={handleUpdate}
      expense={editingExpense}
      onChange={(e) =>
        setEditingExpense({
          ...editingExpense,
          [e.target.name]: e.target.value,
        })
      }
      months={months}
      years={years}
      categories={categories}
    />


      <DeleteModal
        isOpen={showDeleteModal}
        onCancel={() => setShowDeleteModal(false)}
        onConfirm={handleDelete}
      />

      <CopyModal
        isOpen={copyState.show}
        onCancel={() => setCopyState(prev => ({ ...prev, show: false }))}
        onConfirm={handleCopy}
        expense={copyState.expense}
        months={months}
        years={years}
        targetMonth={copyState.targetMonth}
        setTargetMonth={(value) => setCopyState(prev => ({ ...prev, targetMonth: value }))}
        targetYear={copyState.targetYear}
        setTargetYear={(value) => setCopyState(prev => ({ ...prev, targetYear: value }))}
      />
    </div>
  );
}
