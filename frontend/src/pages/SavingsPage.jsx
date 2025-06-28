import { useEffect, useState } from 'react';
import { Trash2, Wrench } from 'lucide-react';

export default function SavingsPage() {
  const [savings, setSavings] = useState([]);
  const [months, setMonths] = useState([]);
  const [years, setYears] = useState([]);
  const [newSaving, setNewSaving] = useState({ name: '', amount: '', month_id: '', year_id: '' });
  const [showModal, setShowModal] = useState(false);
  const [savingToDelete, setSavingToDelete] = useState(null);
  const [search, setSearch] = useState(localStorage.getItem('savingsSearch') || '');
  const [sort, setSort] = useState(localStorage.getItem('savingsSort') || '');
  const [filterMonth, setFilterMonth] = useState(localStorage.getItem('savingsMonth') || '');
  const [filterYear, setFilterYear] = useState(localStorage.getItem('savingsYear') || '');

  const fetchSavings = async () => {
    const res = await fetch('/api/savings');
    if (res.ok) {
      const data = await res.json();
      setSavings(data);
    }
  };

  useEffect(() => {
    fetchSavings();
    fetch('/api/months').then(res => res.json()).then(setMonths);
    fetch('/api/years').then(res => res.json()).then(setYears);
  }, []);

  useEffect(() => {
    localStorage.setItem('savingsSearch', search);
  }, [search]);

  useEffect(() => {
    localStorage.setItem('savingsSort', sort);
  }, [sort]);

  useEffect(() => {
    localStorage.setItem('savingsMonth', filterMonth);
  }, [filterMonth]);

  useEffect(() => {
    localStorage.setItem('savingsYear', filterYear);
  }, [filterYear]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewSaving(prev => ({ ...prev, [name]: value }));
  };

  const handleAddSaving = async () => {
    if (!newSaving.name || !newSaving.amount || !newSaving.month_id || !newSaving.year_id) return;

    const res = await fetch('/api/savings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newSaving)
    });

    if (res.ok) {
      const updated = await res.json();
      setSavings(updated);
      setNewSaving({ name: '', amount: '', month_id: '', year_id: '' });
      setShowModal(false);
    }
  };

  const handleEditClick = (saving) => {
    setNewSaving({
      id: saving.id,
      name: saving.name,
      amount: saving.amount,
      month_id: saving.month_id,
      year_id: saving.year_id
    });
    setShowModal(true);
  };

  const handleUpdateSaving = async () => {
    if (!newSaving.id || !newSaving.name || !newSaving.amount || !newSaving.month_id || !newSaving.year_id) return;

    const res = await fetch(`/api/savings/${newSaving.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newSaving)
    });

    if (res.ok) {
      const updated = await res.json();
      setSavings(updated);
      setShowModal(false);
      setNewSaving({ name: '', amount: '', month_id: '', year_id: '' });
    }
  };

  const handleDeleteSaving = async () => {
    const res = await fetch(`/api/savings/${savingToDelete.id}`, { method: 'DELETE' });
    if (res.ok) {
      const updated = await res.json();
      setSavings(updated);
    }
    setSavingToDelete(null);
  };

  const filtered = savings
    .filter(s =>
      s.name.toLowerCase().includes(search.toLowerCase()) &&
      (filterMonth === '' || s.month_id === parseInt(filterMonth)) &&
      (filterYear === '' || s.year_id === parseInt(filterYear))
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
      <h2 className="text-2xl font-bold text-gray-800">Savings</h2>

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
            Add Saving
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
            {filtered.map((s, i) => (
              <tr key={i} className="border-t hover:bg-gray-50">
                <td className="p-3">{s.name}</td>
                <td className="p-3 text-green-600 font-medium">{parseFloat(s.amount).toFixed(2)} €</td>
                <td className="p-3">{s.month_name}</td>
                <td className="p-3">{s.year_value}</td>
                <td className="p-3 text-right">
                  <div className="inline-flex gap-1">
                    <button className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600" onClick={() => handleEditClick(s)} title="Edit">
                      <Wrench size={16} />
                    </button>
                    <button className="p-2 bg-red-500 text-white rounded hover:bg-red-600" onClick={() => setSavingToDelete(s)} title="Delete">
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
            <h3 className="text-lg font-semibold">{newSaving.id ? 'Edit Saving' : 'Add Saving'}</h3>
            <div className="grid md:grid-cols-4 gap-4">
              <input name="name" value={newSaving.name} onChange={handleInputChange} placeholder="Name" className="border rounded px-3 py-2" />
              <input name="amount" value={newSaving.amount} onChange={handleInputChange} placeholder="Amount" type="number" className="border rounded px-3 py-2" />
              <select name="month_id" value={newSaving.month_id} onChange={handleInputChange} className="border rounded px-3 py-2">
                <option value="">Month</option>
                {months.map(m => (
                  <option key={m.id} value={m.id}>{m.name}</option>
                ))}
              </select>
              <select name="year_id" value={newSaving.year_id} onChange={handleInputChange} className="border rounded px-3 py-2">
                <option value="">Year</option>
                {years.map(y => (
                  <option key={y.id} value={y.id}>{y.value}</option>
                ))}
              </select>
            </div>
            <div className="flex justify-end gap-4">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 border rounded text-gray-600">Cancel</button>
              <button onClick={() => newSaving.id ? handleUpdateSaving() : handleAddSaving()} className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">{newSaving.id ? 'Update' : 'Add'}</button>
            </div>
          </div>
        </div>
      )}

      {savingToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-xl shadow-xl w-full max-w-md">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Confirm Delete</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete <strong>{savingToDelete?.name}</strong>?
            </p>
            <div className="flex justify-end gap-4">
              <button className="px-4 py-2 rounded border text-gray-600 hover:bg-gray-100" onClick={() => setSavingToDelete(null)}>Cancel</button>
              <button className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700" onClick={handleDeleteSaving}>Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
