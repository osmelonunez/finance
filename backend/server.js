const express = require('express');
const cors = require('cors');
const pool = require('./db');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

app.get('/api/expenses', async (req, res) => {
  const result = await pool.query('SELECT * FROM expenses');
  res.json(result.rows);
});

app.post('/api/expenses', async (req, res) => {
  const { name, cost, month, year } = req.body;
  await pool.query('INSERT INTO expenses (name, cost, month, year) VALUES ($1, $2, $3, $4)', [name, cost, month, year]);
  const result = await pool.query('SELECT * FROM expenses');
  res.json(result.rows);
});

app.put('/api/expenses/:id', async (req, res) => {
  const { id } = req.params;
  const { name, cost, month, year } = req.body;
  await pool.query('UPDATE expenses SET name=$1, cost=$2, month=$3, year=$4 WHERE id=$5', [name, cost, month, year, id]);
  const result = await pool.query('SELECT * FROM expenses');
  res.json(result.rows);
});

app.delete('/api/expenses/:id', async (req, res) => {
  const { id } = req.params;
  await pool.query('DELETE FROM expenses WHERE id=$1', [id]);
  const result = await pool.query('SELECT * FROM expenses');
  res.json(result.rows);
});

app.post('/api/incomes', async (req, res) => {
  const { name, amount, month, year } = req.body;
  await pool.query('INSERT INTO incomes (name, amount, month, year) VALUES ($1, $2, $3, $4)', [name, amount, month, year]);
  const result = await pool.query('SELECT * FROM incomes');
  res.json(result.rows);
});

app.put('/api/incomes/:id', async (req, res) => {
  const { id } = req.params;
  const { name, amount, month, year } = req.body;
  await pool.query('UPDATE incomes SET name=$1, amount=$2, month=$3, year=$4 WHERE id=$5', [name, amount, month, year, id]);
  const result = await pool.query('SELECT * FROM incomes');
  res.json(result.rows);
});

app.delete('/api/incomes/:id', async (req, res) => {
  const { id } = req.params;
  await pool.query('DELETE FROM incomes WHERE id=$1', [id]);
  const result = await pool.query('SELECT * FROM incomes');
  res.json(result.rows);
});

app.get('/api/incomes', async (req, res) => {
  const result = await pool.query('SELECT * FROM incomes');
  res.json(result.rows);
});

app.listen(process.env.PORT, () => {
  console.log(`Backend listening on port ${process.env.PORT}`);
});
