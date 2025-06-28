import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, Legend } from 'recharts';

export default function DashboardPage() {
  const [incomes, setIncomes] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [savings, setSavings] = useState([]);
  const [filters, setFilters] = useState({ month: '', year: '' });

  useEffect(() => {
    async function fetchData() {
      const resIncomes = await fetch('/api/incomes');
      const resExpenses = await fetch('/api/expenses');
      const resSavings = await fetch('/api/savings');
      const incomesData = await resIncomes.json();
      const expensesData = await resExpenses.json();
      const savingsData = await resSavings.json();
      setIncomes(incomesData);
      setExpenses(expensesData);
      setSavings(savingsData);
    }
    fetchData();
  }, []);

  const filteredIncomes = incomes.filter(i => (!filters.month || parseInt(i.month) === parseInt(filters.month)) && (!filters.year || parseInt(i.year) === parseInt(filters.year)));
  const filteredExpenses = expenses.filter(e => (!filters.month || parseInt(e.month) === parseInt(filters.month)) && (!filters.year || parseInt(e.year) === parseInt(filters.year)));
  const filteredSavings = savings.filter(s => (!filters.month || parseInt(s.month) === parseInt(filters.month)) && (!filters.year || parseInt(s.year) === parseInt(filters.year)));

  const totalIncome = filteredIncomes.reduce((sum, i) => sum + parseFloat(i.amount), 0);
  const totalExpenses = filteredExpenses.reduce((sum, e) => sum + parseFloat(e.cost), 0);
  const totalSavings = filteredSavings.reduce((sum, s) => sum + parseFloat(s.amount), 0);
  const balance = totalIncome - totalExpenses - totalSavings;

  const groupedData = Array.from({ length: 12 }, (_, month) => {
    const incomeMonth = incomes.filter(i => parseInt(i.month) === month + 1 && (!filters.year || parseInt(i.year) === parseInt(filters.year))).reduce((sum, i) => sum + parseFloat(i.amount), 0);
    const expenseMonth = expenses.filter(e => parseInt(e.month) === month + 1 && (!filters.year || parseInt(e.year) === parseInt(filters.year))).reduce((sum, e) => sum + parseFloat(e.cost), 0);
    const savingMonth = savings.filter(s => parseInt(s.month) === month + 1 && (!filters.year || parseInt(s.year) === parseInt(filters.year))).reduce((sum, s) => sum + parseFloat(s.amount), 0);
    return {
      name: new Date(0, month).toLocaleString('en', { month: 'short' }),
      income: parseFloat(incomeMonth.toFixed(2)),
      expense: parseFloat(expenseMonth.toFixed(2)),
      saving: parseFloat(savingMonth.toFixed(2)),
      balance: parseFloat((incomeMonth - expenseMonth).toFixed(2))
    };
  });

  const COLORS = ['#10b981', '#ef4444', '#fbbf24', '#3b82f6'];

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-wrap gap-4 mb-4">
        <select name="month" onChange={(e) => setFilters(prev => ({ ...prev, month: e.target.value }))} className="border px-4 py-2 rounded">
          <option value="">All Months</option>
          {[...Array(12)].map((_, i) => (
            <option key={i + 1} value={i + 1}>{new Date(0, i).toLocaleString('en', { month: 'long' })}</option>
          ))}
        </select>
        <select name="year" onChange={(e) => setFilters(prev => ({ ...prev, year: e.target.value }))} className="border px-4 py-2 rounded">
          <option value="">All Years</option>
          {Array.from({ length: 6 }, (_, i) => 2025 + i).map(y => <option key={y}>{y}</option>)}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-2 rounded shadow text-center text-sm">
          <h3 className="text-sm text-gray-500">Total Incomes</h3>
          <p className="text-xl text-green-600 font-bold">{totalIncome.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })}</p>
        </div>
        <div className="bg-white p-2 rounded shadow text-center text-sm">
          <h3 className="text-sm text-gray-500">Total Expenses</h3>
          <p className="text-xl text-red-600 font-bold">{totalExpenses.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })}</p>
        </div>
        <div className="bg-white p-2 rounded shadow text-center text-sm">
          <h3 className="text-sm text-gray-500">Savings</h3>
          <p className="text-xl text-amber-600 font-bold">{totalSavings.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })}</p>
        </div>
        <div className="bg-white p-2 rounded shadow text-center text-sm">
          <h3 className="text-sm text-gray-500">Balance</h3>
          <p className="text-xl text-blue-600 font-bold">{balance.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-4 rounded shadow">
          <h3 className="text-sm text-gray-600 mb-2">Income vs. Expenses (Line)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={groupedData}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="income" stroke="#10b981" strokeWidth={2} />
              <Line type="monotone" dataKey="expense" stroke="#ef4444" strokeWidth={2} />
              <Line type="monotone" dataKey="saving" stroke="#fbbf24" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-4 rounded shadow">
          <h3 className="text-sm text-gray-600 mb-2">Incomes, Expenses, Balance (Donut)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                dataKey="value"
                data={[{ name: 'Incomes', value: totalIncome }, { name: 'Expenses', value: totalExpenses }, { name: 'Savings', value: totalSavings }, { name: 'Balance', value: balance }]}
                cx="50%"
                cy="50%"
                outerRadius={90}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(2)}%`}
              >
                {COLORS.map((color, index) => (
                  <Cell key={index} fill={color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white p-4 rounded shadow">
        <h3 className="text-sm text-gray-600 mb-2">Income vs. Expenses vs. Savings vs. Balance (Bar)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={groupedData}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="income" fill="#10b981" name="Incomes" />
            <Bar dataKey="expense" fill="#ef4444" name="Expenses" />
            <Bar dataKey="saving" fill="#fbbf24" name="Savings" />
            <Bar dataKey="balance" fill="#3b82f6" name="Balance" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
