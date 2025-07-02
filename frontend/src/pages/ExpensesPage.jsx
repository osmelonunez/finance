import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Trash2, Wrench, CopyPlus  } from 'lucide-react';
import FiltersBar from '../components/expenses/FiltersBar';
import ExpensesTable from '../components/expenses/ExpensesTable';
import DeleteModal from '../components/expenses/DeleteModal';




export default function ExpensesPage() {
  const navigate = useNavigate();
  const [expenses, setExpenses] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [filters, setFilters] = useState({ month_id: '', year_id: '', category_id: '' });
  const [categories, setCategories] = useState([]);
  const [months, setMonths] = useState([]);
  const [years, setYears] = useState([]);
  const [newExpense, setNewExpense] = useState({ name: '', cost: '', month_id: '', year_id: '', category_id: '' });
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [expenseToDelete, setExpenseToDelete] = useState(null);
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('');

  useEffect(() => {
    fetch('/api/expenses', {
  headers: {
    Authorization: `Bearer ${localStorage.getItem('token')}`
  }
})
      .then(res => res.json())
      .then(data => {
        setExpenses(data);
        setFiltered(data);
      });

    fetch('/api/categories', {
  headers: {
    Authorization: `Bearer ${localStorage.getItem('token')}`
  }
})
      .then(res => res.json())
      .then(data => {
        const sorted = data.sort((a, b) => a.name.localeCompare(b.name));
        setCategories(sorted);
      });

    fetch('/api/months', {
  headers: {
    Authorization: `Bearer ${localStorage.getItem('token')}`
  }
})
      .then(res => res.json())
      .then(setMonths);

    fetch('/api/years', {
  headers: {
    Authorization: `Bearer ${localStorage.getItem('token')}`
  }
})
      .then(res => res.json())
      .then(setYears);
  }, []);

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
    if (!newExpense.name || !newExpense.cost || !newExpense.month_id || !newExpense.year_id || !newExpense.category_id) return;

    const res = await fetch('/api/expenses', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newExpense)
    });

    if (res.ok) {
      const updated = await res.json();
      setExpenses(updated);
      setNewExpense({ id: '', name: '', cost: '', month_id: '', year_id: '', category_id: '' });
      setShowModal(false);
    }
  };

  const handleEditClick = (expense) => {
    setNewExpense({ ...expense });
    setShowModal(true);
  };

  const handleUpdateExpense = async () => {
    if (!newExpense.id || !newExpense.name || !newExpense.cost || !newExpense.month_id || !newExpense.year_id || !newExpense.category_id) return;

    const res = await fetch(`/api/expenses/${newExpense.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newExpense)
    });

    if (res.ok) {
      const updated = await res.json();
      setExpenses(updated);
      setShowModal(false);
      setNewExpense({ id: '', name: '', cost: '', month_id: '', year_id: '', category_id: '' });
    }
  };

  const handleDeleteExpense = (expense) => {
    setExpenseToDelete(expense);
    setShowDeleteModal(true);
  };

  const confirmDeleteExpense = async () => {
    if (!expenseToDelete) return;
    const res = await fetch(`/api/expenses/${expenseToDelete.id}`, { method: 'DELETE' });
    if (res.ok) {
      const updated = await res.json();
      setExpenses(updated);
    }
    setShowDeleteModal(false);
    setExpenseToDelete(null);
  };

  const [currentPage, setCurrentPage] = useState(1);
const [showCopyModal, setShowCopyModal] = useState(false);
  const [copyExpenseData, setCopyExpenseData] = useState(null);

const [copyTargetMonth, setCopyTargetMonth] = useState('');
const [copyTargetYear, setCopyTargetYear] = useState('');
  const itemsPerPage = 10;
  const totalPages = Math.ceil(filtered.length / itemsPerPage);
  const paginated = filtered.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  
  const handleCopyClick = (expense) => {
    setCopyExpenseData(expense);
    setCopyTargetMonth('');
    setCopyTargetYear('');
    setShowCopyModal(true);
  };

return (
    <div className="space-y-8">
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
        setShowModal={setShowModal}
      />


      <div className="bg-green-100 border border-green-300 rounded-lg p-4 text-right text-green-800 font-semibold">
        Total: {filtered.reduce((acc, e) => acc + parseFloat(e.cost), 0).toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €
      </div>

      <ExpensesTable
        expenses={paginated}
        onEdit={handleEditClick}
        onDelete={handleDeleteExpense}
        onCopy={handleCopyClick}
      />

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-xl w-full max-w-xl shadow-lg space-y-4">
            <h3 className="text-lg font-semibold">{newExpense.id ? "Edit Expense" : "Add Expense"}</h3>
            <div className="grid md:grid-cols-4 gap-4">
              <input name="name" value={newExpense.name} onChange={handleInputChange} placeholder="Name" className="border rounded px-3 py-2" />
              <input name="cost" value={newExpense.cost} onChange={handleInputChange} placeholder="Cost" type="number" className="border rounded px-3 py-2" />
              <select name="month_id" value={newExpense.month_id} onChange={handleInputChange} className="border rounded px-3 py-2">
                <option value="">Month</option>
                {months.map(m => (
                  <option key={m.id} value={m.id}>{m.name}</option>
                ))}
              </select>
              <select name="year_id" value={newExpense.year_id} onChange={handleInputChange} className="border rounded px-3 py-2">
                <option value="">Year</option>
                {years.map(y => (
                  <option key={y.id} value={y.id}>{y.value}</option>
                ))}
              </select>
              <select name="category_id" value={newExpense.category_id} onChange={handleInputChange} className="border rounded px-3 py-2">
                <option value="">Category</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
            </div>
            <div className="flex justify-end gap-4">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 border rounded text-gray-600">Cancel</button>
              <button onClick={() => newExpense.id ? handleUpdateExpense() : handleAddExpense()} className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">{newExpense.id ? "Update" : "Add"}</button>
            </div>
          </div>
        </div>
      )}

      <DeleteModal
        isOpen={showDeleteModal}
        onCancel={() => {
          setShowDeleteModal(false);
          setExpenseToDelete(null);
        }}
        onConfirm={confirmDeleteExpense}
        expense={expenseToDelete}
      />

{showCopyModal && (
  <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
    <div className="bg-white p-6 rounded-xl shadow-xl w-full max-w-md space-y-4">
      <h3 className="text-lg font-semibold">Copy Expense</h3>
      <p className="text-gray-700">
        You're copying: <strong>{copyExpenseData?.name}</strong>
      </p>
      <div className="grid grid-cols-2 gap-4">
        <select value={copyTargetMonth} onChange={e => setCopyTargetMonth(e.target.value)} className="border rounded px-3 py-2">
          <option value="">Select Month</option>
          {months.map(m => (
            <option key={m.id} value={m.id}>{m.name}</option>
          ))}
        </select>
        <select value={copyTargetYear} onChange={e => setCopyTargetYear(e.target.value)} className="border rounded px-3 py-2">
          <option value="">Select Year</option>
          {years.map(y => (
            <option key={y.id} value={y.id}>{y.value}</option>
          ))}
        </select>
      </div>
      <div className="flex justify-end gap-4">
        <button onClick={() => setShowCopyModal(false)} className="px-4 py-2 border rounded text-gray-600">Cancel</button>
        <button
          onClick={() => {
            if (!copyTargetMonth || !copyTargetYear) return;
            const newEntry = {
              name: copyExpenseData.name,
              cost: copyExpenseData.cost,
              month_id: copyTargetMonth,
              year_id: copyTargetYear,
              category_id: copyExpenseData.category_id
            };
            fetch('/api/expenses', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(newEntry)
            })
              .then(res => res.json())
              .then(data => {
                setExpenses(data);
                setShowCopyModal(false);
              });
          }}
          className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700"
        >
          Copy
        </button>
      </div>
    </div>
  </div>
)}
<div className="flex justify-center items-center gap-2 mt-4">
        <button onClick={() => setCurrentPage(p => Math.max(p - 1, 1))} disabled={currentPage === 1} className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50">Prev</button>
        <span className="px-2">Page {currentPage} of {totalPages}</span>
        <button onClick={() => setCurrentPage(p => Math.min(p + 1, totalPages))} disabled={currentPage === totalPages} className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50">Next</button>
      </div>
    </div>
  );
}
