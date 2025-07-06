require('./db'); // fuerza ejecución de inicialización de la BD
const express = require('express');
const cors = require('cors');
require('dotenv').config();

const expensesRoutes = require('./routes/expenses');
const incomeRoutes = require('./routes/income');
const categoryRoutes = require('./routes/category');
const savingsRoutes = require('./routes/savings');
const monthsRoutes = require('./routes/months');
const yearsRoutes = require('./routes/years');
const authRoutes = require('./routes/auth');
const registerRoutes = require('./routes/register');
const emailsRoutes = require('./routes/emails');
const usersRoutes = require('./routes/users');

const app = express();
app.use(cors());
app.use(express.json());

app.use('/api/expenses', expensesRoutes);
app.use('/api/incomes', incomeRoutes);
app.use('/api/categories', categoryRoutes);
app.use('/api/savings', savingsRoutes);
app.use('/api/months', monthsRoutes);
app.use('/api/years', yearsRoutes);
app.use('/api', authRoutes);        // /api/login, /api/me
app.use('/api/register', registerRoutes);
app.use('/api/emails', emailsRoutes);
app.use('/api/users', usersRoutes);


app.listen(process.env.BACKEND_PORT, '0.0.0.0', () => {
  console.log(`Backend listening on port ${process.env.BACKEND_PORT}`);
});
