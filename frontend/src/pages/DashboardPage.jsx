import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, Legend } from 'recharts';

export default function DashboardPage() {
  const [incomes, setIncomes] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [savings, setSavings] = useState([]);
  const [months, setMonths] = useState([]);
  const [years, setYears] = useState([]);
  const [filters, setFilters] = useState({ month_id: '', year_id: '' });

  useEffect(() => {
    async function fetchData() {
      const [resIncomes, resExpenses, resSavings, resMonths, resYears] = await Promise.all([
        fetch('/api/incomes'),
        fetch('/api/expenses'),
        fetch('/api/savings'),
        fetch('/api/months'),
        fetch('/api/years')
      ]);
      const [incomesData, expensesData, savingsData, monthsData, yearsData] = await Promise.all([
        resIncomes.json(),
        resExpenses.json(),
        resSavings.json(),
        resMonths.json(),
        resYears.json()
      ]);
      setIncomes(incomesData);
      setExpenses(expensesData);
      setSavings(savingsData);
      setMonths(monthsData);
      setYears(yearsData);
    }
    fetchData();
  }, []);

  const filteredIncomes = incomes.filter(i => (!filters.month_id || i.month_id === parseInt(filters.month_id)) && (!filters.year_id || i.year_id === parseInt(filters.year_id)));
  const filteredExpenses = expenses.filter(e => (!filters.month_id || e.month_id === parseInt(filters.month_id)) && (!filters.year_id || e.year_id === parseInt(filters.year_id)));
  const filteredSavings = savings.filter(s => (!filters.month_id || s.month_id === parseInt(filters.month_id)) && (!filters.year_id || s.year_id === parseInt(filters.year_id)));

  const totalIncome = filteredIncomes.reduce((sum, i) => sum + parseFloat(i.amount), 0);
  const totalExpenses = filteredExpenses.reduce((sum, e) => sum + parseFloat(e.cost), 0);
  const totalSavings = filteredSavings.reduce((sum, s) => sum + parseFloat(s.amount), 0);
  const balance = totalIncome - totalExpenses - totalSavings;

  const groupedData = months.map(m => {
    const incomeMonth = incomes.filter(i => i.month_id === m.id && (!filters.year_id || i.year_id === parseInt(filters.year_id))).reduce((sum, i) => sum + parseFloat(i.amount), 0);
    const expenseMonth = expenses.filter(e => e.month_id === m.id && (!filters.year_id || e.year_id === parseInt(filters.year_id))).reduce((sum, e) => sum + parseFloat(e.cost), 0);
    const savingMonth = savings.filter(s => s.month_id === m.id && (!filters.year_id || s.year_id === parseInt(filters.year_id))).reduce((sum, s) => sum + parseFloat(s.amount), 0);
    return {
      name: m.name.substring(0, 3),
      income: parseFloat(incomeMonth.toFixed(2)),
      expense: parseFloat(expenseMonth.toFixed(2)),
      saving: parseFloat(savingMonth.toFixed(2)),
      balance: parseFloat((incomeMonth - expenseMonth - savingMonth).toFixed(2))
    };
  });

  const COLORS = ['#10b981', '#ef4444', '#fbbf24', '#3b82f6'];

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-wrap gap-4 mb-4">
        <select name="month_id" onChange={(e) => setFilters(prev => ({ ...prev, month_id: e.target.value }))} className="border px-4 py-2 rounded">
          <option value="">All Months</option>
          {months.map(m => (
            <option key={m.id} value={m.id}>{m.name}</option>
          ))}
        </select>
        <select name="year_id" onChange={(e) => setFilters(prev => ({ ...prev, year_id: e.target.value }))} className="border px-4 py-2 rounded">
          <option value="">All Years</option>
          {years.map(y => (
            <option key={y.id} value={y.id}>{y.value}</option>
          ))}
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
