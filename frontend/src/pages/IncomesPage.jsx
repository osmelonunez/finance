import { useEffect, useState } from 'react';
import { Trash2, Wrench, FilePlus } from 'lucide-react';

export default function IncomesPage() {
  const [incomes, setIncomes] = useState([]);
  const [months, setMonths] = useState([]);
  const [years, setYears] = useState([]);
  const [newIncome, setNewIncome] = useState({ name: '', amount: '', month_id: '', year_id: '' });
  const [showModal, setShowModal] = useState(false);
  const [incomeToDelete, setIncomeToDelete] = useState(null);
  const [search, setSearch] = useState(localStorage.getItem('incomesSearch') || '');
  const [sort, setSort] = useState(localStorage.getItem('incomesSort') || '');
  const [filterMonth, setFilterMonth] = useState(localStorage.getItem('incomesMonth') || '');
  const [filterYear, setFilterYear] = useState(localStorage.getItem('incomesYear') || '');

  const fetchIncomes = async () => {
    const res = await fetch('/api/incomes');
    if (res.ok) {
      const data = await res.json();
      setIncomes(data);
    }
  };

  useEffect(() => {
    fetchIncomes();
    fetch('/api/months').then(res => res.json()).then(setMonths);
    fetch('/api/years').then(res => res.json()).then(setYears);
  }, []);

  useEffect(() => localStorage.setItem('incomesSearch', search), [search]);
  useEffect(() => localStorage.setItem('incomesSort', sort), [sort]);
  useEffect(() => localStorage.setItem('incomesMonth', filterMonth), [filterMonth]);
  useEffect(() => localStorage.setItem('incomesYear', filterYear), [filterYear]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewIncome(prev => ({ ...prev, [name]: value }));
  };

  const handleAddIncome = async () => {
    if (!newIncome.name || !newIncome.amount || !newIncome.month_id || !newIncome.year_id) return;

    const res = await fetch('/api/incomes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newIncome)
    });

    if (res.ok) {
      const updated = await res.json();
      setIncomes(updated);
      setNewIncome({ name: '', amount: '', month_id: '', year_id: '' });
      setShowModal(false);
    }
  };

  const handleEditClick = (income) => {
    setNewIncome({
      id: income.id,
      name: income.name,
      amount: income.amount,
      month_id: income.month_id,
      year_id: income.year_id
    });
    setShowModal(true);
  };

  const handleCopyClick = (income) => {
    const name = income.name;
    const amount = income.amount;
    const targetMonth = prompt("Enter target month ID (1–12):");
    const targetYear = prompt("Enter target year ID:");

    if (!targetMonth || !targetYear) return;

    const newEntry = {
      name,
      amount,
      month_id: targetMonth,
      year_id: targetYear
    };

    fetch('/api/incomes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newEntry)
    }).then(res => res.json())
      .then(setIncomes);
  };

  const handleUpdateIncome = async () => {
    if (!newIncome.id || !newIncome.name || !newIncome.amount || !newIncome.month_id || !newIncome.year_id) return;

    const res = await fetch(`/api/incomes/${newIncome.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newIncome)
    });

    if (res.ok) {
      const updated = await res.json();
      setIncomes(updated);
      setShowModal(false);
      setNewIncome({ name: '', amount: '', month_id: '', year_id: '' });
    }
  };

  const handleDeleteIncome = async () => {
    const res = await fetch(`/api/incomes/${incomeToDelete.id}`, { method: 'DELETE' });
    if (res.ok) {
      const updated = await res.json();
      setIncomes(updated);
    }
    setIncomeToDelete(null);
  };

  const filtered = incomes
    .filter(e =>
      e.name.toLowerCase().includes(search.toLowerCase()) &&
      (filterMonth === '' || e.month_id === parseInt(filterMonth)) &&
      (filterYear === '' || e.year_id === parseInt(filterYear))
    )
    .sort((a, b) => {
      if (sort === 'amount') return b.amount - a.amount;
      if (sort === 'month') return a.month_id - b.month_id;
      if (sort === 'year') return a.year_id - b.year_id;
      if (sort === 'name') return a.name.localeCompare(b.name);
      return 0;
    });

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold text-gray-800">Incomes</h2>

      <div className="bg-white p-6 rounded-xl shadow space-y-4">
        <div className="flex flex-wrap justify-between items-center gap-2">
          <div className="flex gap-2 flex-wrap items-center">
            <select value={sort} onChange={e => setSort(e.target.value)} className="border rounded px-3 py-2">
              <option value="">Sort by</option>
              <option value="name">Name</option>
              <option value="amount">Amount</option>
              <option value="month">Month</option>
              <option value="year">Year</option>
            </select>
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search by name..."
              className="border rounded px-3 py-2 w-44"
            />
            <select value={filterMonth} onChange={e => setFilterMonth(e.target.value)} className="border rounded px-3 py-2">
              <option value="">All Months</option>
              {months.map(m => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
            <select value={filterYear} onChange={e => setFilterYear(e.target.value)} className="border rounded px-3 py-2">
              <option value="">All Years</option>
              {years.map(y => (
                <option key={y.id} value={y.id}>{y.value}</option>
              ))}
            </select>
          </div>
          <button onClick={() => setShowModal(true)} className="bg-green-600 text-white px-5 py-2 rounded hover:bg-blue-700">
            Add Income
          </button>
        </div>

        <table className="min-w-full bg-white shadow rounded-xl">
          <thead className="bg-gray-50 text-left">
            <tr>
              <th className="p-3">Name</th>
              <th className="p-3">Amount</th>
              <th className="p-3">Month</th>
              <th className="p-3">Year</th>
              <th className="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((e, i) => (
              <tr key={i} className="border-t hover:bg-gray-50">
                <td className="p-3">{e.name}</td>
                <td className="p-3 text-green-600 font-medium">{parseFloat(e.amount).toFixed(2)} €</td>
                <td className="p-3">{e.month_name}</td>
                <td className="p-3">{e.year_value}</td>
                <td className="p-3 text-right">
                  <div className="inline-flex gap-1">
                    <button className="p-2 bg-gray-400 text-white rounded hover:bg-gray-500" onClick={() => handleCopyClick(e)} title="Copy">
                      <FilePlus size={16} />
                    </button>
                    <button className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600" onClick={() => handleEditClick(e)} title="Edit">
                      <Wrench size={16} />
                    </button>
                    <button className="p-2 bg-red-500 text-white rounded hover:bg-red-600" onClick={() => setIncomeToDelete(e)} title="Delete">
                      <Trash2 size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-xl w-full max-w-xl shadow-lg space-y-4">
            <h3 className="text-lg font-semibold">{newIncome.id ? 'Edit Income' : 'Add Income'}</h3>
            <div className="grid md:grid-cols-4 gap-4">
              <input name="name" value={newIncome.name} onChange={handleInputChange} placeholder="Name" className="border rounded px-3 py-2" />
              <input name="amount" value={newIncome.amount} onChange={handleInputChange} placeholder="Amount" type="number" className="border rounded px-3 py-2" />
              <select name="month_id" value={newIncome.month_id} onChange={handleInputChange} className="border rounded px-3 py-2">
                <option value="">Month</option>
                {months.map(m => (
                  <option key={m.id} value={m.id}>{m.name}</option>
                ))}
              </select>
              <select name="year_id" value={newIncome.year_id} onChange={handleInputChange} className="border rounded px-3 py-2">
                <option value="">Year</option>
                {years.map(y => (
                  <option key={y.id} value={y.id}>{y.value}</option>
                ))}
              </select>
            </div>
            <div className="flex justify-end gap-4">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 border rounded text-gray-600">Cancel</button>
              <button onClick={() => newIncome.id ? handleUpdateIncome() : handleAddIncome()} className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">{newIncome.id ? 'Update' : 'Add'}</button>
            </div>
          </div>
        </div>
      )}

      {incomeToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-xl shadow-xl w-full max-w-md">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Confirm Delete</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete <strong>{incomeToDelete?.name}</strong>?
            </p>
            <div className="flex justify-end gap-4">
              <button className="px-4 py-2 rounded border text-gray-600 hover:bg-gray-100" onClick={() => setIncomeToDelete(null)}>Cancel</button>
              <button className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700" onClick={handleDeleteIncome}>Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
