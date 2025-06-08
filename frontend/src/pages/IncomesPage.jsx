import { useEffect, useState } from 'react';
import { Trash2, Wrench } from 'lucide-react';

export default function IncomesPage() {
  const [incomes, setIncomes] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [filters, setFilters] = useState({ month: '', year: '' });
  const [newIncome, setNewIncome] = useState({ name: '', amount: '', month: '', year: '' });
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [incomeToDelete, setIncomeToDelete] = useState(null);

  useEffect(() => {
    fetch('/api/incomes')
      .then(res => res.json())
      .then(data => {
        setIncomes(data);
        setFiltered(data);

        data.sort((a, b) => {
          if (a.year !== b.year) return a.year - b.year;
          if (a.month !== b.month) return a.month - b.month;
          return parseFloat(b.amount) - parseFloat(a.amount);
        });
      });
  }, []);

  useEffect(() => {
    let result = [...incomes];
    if (filters.month) result = result.filter(e => parseInt(e.month) === parseInt(filters.month));
    if (filters.year) result = result.filter(e => parseInt(e.year) === parseInt(filters.year));
    setFiltered(result);
  }, [filters, incomes]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewIncome(prev => ({ ...prev, [name]: value }));
  };

  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  const totalPages = Math.ceil(filtered.length / itemsPerPage);
  const paginated = filtered.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handleEditClick = (income) => {
    setNewIncome({ ...income });
    setShowModal(true);
  };

  const handleDeleteIncome = (income) => {
    setIncomeToDelete(income);
    setShowDeleteModal(true);
  };

  const confirmDeleteIncome = async () => {
    if (!incomeToDelete) return;
    const res = await fetch(`/api/incomes/${incomeToDelete.id}`, { method: 'DELETE' });
    if (res.ok) {
      const updated = await res.json();
      setIncomes(updated);
    }
    setShowDeleteModal(false);
    setIncomeToDelete(null);
  };

  const handleUpdateIncome = async () => {
    if (!newIncome.id || !newIncome.name || !newIncome.amount || !newIncome.month || !newIncome.year) return;

    const res = await fetch(`/api/incomes/${newIncome.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newIncome)
    });

    if (res.ok) {
      const updated = await res.json();
      setIncomes(updated);
      setNewIncome({ id: '', name: '', amount: '', month: '', year: '' });
      setShowModal(false);
    }
  };

  const handleAddIncome = async () => {
    if (!newIncome.name || !newIncome.amount || !newIncome.month || !newIncome.year) return;

    const res = await fetch('/api/incomes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newIncome)
    });

    if (res.ok) {
      const updated = await res.json();
      setIncomes(updated);
      setNewIncome({ name: '', amount: '', month: '', year: '' });
      setShowModal(false);
    }
  };

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold text-gray-800">Incomes</h2>

      <div className="bg-white p-6 rounded-xl shadow space-y-4">
        <div className="flex flex-wrap gap-4 items-center">
          <select
            name="sort"
            className="border rounded px-3 py-2"
            onChange={(e) => {
              const val = e.target.value;
              const sorted = [...filtered];
              if (val === "name") sorted.sort((a, b) => a.name.localeCompare(b.name));
              if (val === "amount") sorted.sort((a, b) => parseFloat(b.amount) - parseFloat(a.amount));
              if (val === "month") sorted.sort((a, b) => a.month - b.month);
              if (val === "year") sorted.sort((a, b) => a.year - b.year);
              if (val === "ymamount") {
                sorted.sort((a, b) => {
                  if (a.year !== b.year) return a.year - b.year;
                  if (a.month !== b.month) return a.month - b.month;
                  return parseFloat(b.amount) - parseFloat(a.amount);
                });
              } else if (val === "ymname") {
                sorted.sort((a, b) => {
                  if (a.year !== b.year) return a.year - b.year;
                  if (a.month !== b.month) return a.month - b.month;
                  return a.name.localeCompare(b.name);
                });
              }
              setFiltered(sorted);
            }}
          >
            <option value="">Sort by</option>
            <option value="name">Name</option>
            <option value="amount">Amount</option>
            <option value="month">Month</option>
            <option value="year">Year</option>
            <option value="ymamount">Y-M-Amount</option>
            <option value="ymname">Y-M-Name</option>
          </select>

          <input
            type="text"
            name="search"
            placeholder="Search by name..."
            className="border rounded px-3 py-2 w-60"
            onChange={(e) => {
              const term = e.target.value.toLowerCase();
              const filteredList = incomes.filter(exp =>
                exp.name.toLowerCase().includes(term)
              );
              setFiltered(filteredList);
            }}
          />
          <select name="month" value={filters.month} onChange={handleFilterChange} className="border rounded px-3 py-2">
            <option value="">All Months</option>
            {[...Array(12)].map((_, i) => (
              <option key={i + 1} value={i + 1}>{new Date(0, i).toLocaleString('en', { month: 'long' })}</option>
            ))}
          </select>
          <select name="year" value={filters.year} onChange={handleFilterChange} className="border rounded px-3 py-2">
            <option value="">All Years</option>
            {[2025, 2026, 2027, 2028, 2029, 2030].map(y => <option key={y}>{y}</option>)}
          </select>

          <button onClick={() => setShowModal(true)} className="bg-green-600 text-white px-6 py-2 rounded hover:bg-blue-700 ml-auto">
            Add Income
          </button>
        </div>
      </div>

      <div className="bg-green-100 border border-green-300 rounded-lg p-4 text-right text-green-800 font-semibold">
        Total: {filtered.reduce((acc, e) => acc + parseFloat(e.amount), 0).toLocaleString('es-ES', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        })} €
      </div>

      <table className="min-w-full bg-white shadow rounded-xl">
        <thead className="bg-gray-50 text-left">
          <tr>
            <th className="p-3">Name</th>
            <th className="p-3">Amount</th>
            <th className="p-3">Month</th>
            <th className="p-3">Year</th>
            <th className="p-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          {paginated.map((e, i) => (
            <tr key={i} className="border-t hover:bg-gray-50">
              <td className="p-3">{e.name}</td>
              <td className="p-3 text-red-500 font-medium">{parseFloat(e.amount).toLocaleString('es-ES', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
              })} €</td>
              <td className="p-3">{new Date(0, e.month - 1).toLocaleString('en', { month: 'long' })}</td>
              <td className="p-3">{e.year}</td>
              <td className="p-3">
                <div className="inline-flex gap-1">
                  <button
                    className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    onClick={() => handleEditClick(e)}
                    title="Editar"
                  >
                    <Wrench size={16} />
                  </button>
                  <button
                    className="p-2 bg-red-500 text-white rounded hover:bg-red-600"
                    onClick={() => handleDeleteIncome(e)}
                    title="Eliminar"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-xl w-full max-w-xl shadow-lg space-y-4">
            <h3 className="text-lg font-semibold">{newIncome.id ? "Edit Income" : "Add Income"}</h3>
            <div className="grid md:grid-cols-4 gap-4">
              <input name="name" value={newIncome.name} onChange={handleInputChange} placeholder="Name" className="border rounded px-3 py-2" />
              <input name="amount" value={newIncome.amount} onChange={handleInputChange} placeholder="Amount" type="number" className="border rounded px-3 py-2" />
              <select name="month" value={newIncome.month} onChange={handleInputChange} className="border rounded px-3 py-2">
                <option value="">Month</option>
                {[...Array(12)].map((_, i) => (
                  <option key={i + 1} value={i + 1}>{new Date(0, i).toLocaleString('en', { month: 'long' })}</option>
                ))}
              </select>
              <select name="year" value={newIncome.year} onChange={handleInputChange} className="border rounded px-3 py-2">
                <option value="">Year</option>
                {[2025, 2026, 2027, 2028, 2029, 2030].map(y => <option key={y}>{y}</option>)}
              </select>
            </div>
            <div className="flex justify-end gap-4">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 border rounded text-gray-600">Cancel</button>
              <button onClick={() => newIncome.id ? handleUpdateIncome() : handleAddIncome()} className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">{newIncome.id ? "Update" : "Add"}</button>
            </div>
          </div>
        </div>
      )}

      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-xl shadow-xl w-full max-w-md">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Confirm Delete</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete <strong>{incomeToDelete?.name}</strong> from{' '}
              <strong>{new Date(0, incomeToDelete?.month - 1).toLocaleString('en', { month: 'long' })} {incomeToDelete?.year}</strong>?
            </p>
            <div className="flex justify-end gap-4">
              <button
                className="px-4 py-2 rounded border text-gray-600 hover:bg-gray-100"
                onClick={() => {
                  setShowDeleteModal(false);
                  setIncomeToDelete(null);
                }}
              >
                Cancel
              </button>
              <button
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                onClick={confirmDeleteIncome}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-center items-center gap-2 mt-4">
        <button
          onClick={() => setCurrentPage(p => Math.max(p - 1, 1))}
          disabled={currentPage === 1}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          Prev
        </button>
        <span className="px-2">Page {currentPage} of {totalPages}</span>
        <button
          onClick={() => setCurrentPage(p => Math.min(p + 1, totalPages))}
          disabled={currentPage === totalPages}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
}
