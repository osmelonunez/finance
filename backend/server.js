const express = require('express');
const cors = require('cors');
const db = require('./db');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

app.get('/api/expenses', async (req, res) => {
  try {
    const result = await db.query(`
      SELECT e.id, e.name, e.cost, e.month, e.year, c.name AS category
      FROM expenses e
      LEFT JOIN categories c ON e.category_id = c.id
      ORDER BY e.year, e.month;
    `);
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to fetch expenses' });
  }
});

app.post('/api/expenses', async (req, res) => {
  try {
    const { name, cost, month, year, category_id } = req.body;
    await db.query(
      'INSERT INTO expenses (name, cost, month, year, category_id) VALUES ($1, $2, $3, $4, $5)',
      [name, cost, month, year, category_id]
    );
    const updated = await db.query(`
      SELECT e.id, e.name, e.cost, e.month, e.year, c.name AS category
      FROM expenses e
      LEFT JOIN categories c ON e.category_id = c.id
      ORDER BY e.year, e.month;
    `);
    res.json(updated.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to add expense' });
  }
});


app.put('/api/expenses/:id', async (req, res) => {
  const { id } = req.params;
  const { name, cost, month, year, category_id } = req.body;

  try {
    await db.query(
      'UPDATE expenses SET name = $1, cost = $2, month = $3, year = $4, category_id = $5 WHERE id = $6',
      [name, cost, month, year, category_id, id]
    );

    const result = await db.query(`
      SELECT e.id, e.name, e.cost, e.month, e.year, c.name AS category
      FROM expenses e
      LEFT JOIN categories c ON e.category_id = c.id
      ORDER BY e.year, e.month;
    `);
    res.json(result.rows);
  } catch (err) {
    console.error('Error updating expense:', err);
    res.status(500).json({ error: 'Failed to update expense' });
  }
});


app.delete('/api/expenses/:id', async (req, res) => {
  const { id } = req.params;

  try {
    await db.query('DELETE FROM expenses WHERE id = $1', [id]);

    const result = await db.query(`
      SELECT e.id, e.name, e.cost, e.month, e.year, c.name AS category
      FROM expenses e
      LEFT JOIN categories c ON e.category_id = c.id
      ORDER BY e.year, e.month;
    `);

    res.json(result.rows);
  } catch (err) {
    console.error('Error deleting expense:', err);
    res.status(500).json({ error: 'Failed to delete expense' });
  }
});


app.post('/api/incomes', async (req, res) => {
  const { name, amount, month, year } = req.body;
  await db.query('INSERT INTO incomes (name, amount, month, year) VALUES ($1, $2, $3, $4)', [name, amount, month, year]);
  const result = await db.query('SELECT * FROM incomes');
  res.json(result.rows);
});

app.put('/api/incomes/:id', async (req, res) => {
  const { id } = req.params;
  const { name, amount, month, year } = req.body;
  await db.query('UPDATE incomes SET name=$1, amount=$2, month=$3, year=$4 WHERE id=$5', [name, amount, month, year, id]);
  const result = await db.query('SELECT * FROM incomes');
  res.json(result.rows);
});

app.delete('/api/incomes/:id', async (req, res) => {
  const { id } = req.params;
  await db.query('DELETE FROM incomes WHERE id=$1', [id]);
  const result = await db.query('SELECT * FROM incomes');
  res.json(result.rows);
});

app.get('/api/incomes', async (req, res) => {
  const result = await db.query('SELECT * FROM incomes');
  res.json(result.rows);
});

app.get('/api/categories', async (req, res) => {
  try {
    const result = await db.query('SELECT id, name FROM categories ORDER BY name');
    console.log('🟢 Categorías obtenidas:', result.rows);
    res.json(result.rows);
  } catch (err) {
    console.error('Error al obtener categorías:', err);
    res.status(500).json({ error: 'Error interno al consultar categorías' });
  }
});


app.post('/api/categories', async (req, res) => {
  const { name } = req.body;
  if (!name?.trim()) return res.status(400).json({ error: 'Nombre inválido' });

  try {
    await db.query('INSERT INTO categories (name) VALUES ($1)', [name.trim()]);
    const result = await db.query('SELECT id, name FROM categories ORDER BY name');
    res.json(result.rows);
  } catch (err) {
    console.error('Error al agregar categoría:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.put('/api/categories/:id', async (req, res) => {
  const { id } = req.params;
  const { name } = req.body;
  if (!name?.trim()) return res.status(400).json({ error: 'Nombre inválido' });

  try {
    await db.query('UPDATE categories SET name = $1 WHERE id = $2', [name.trim(), id]);
    const result = await db.query('SELECT id, name FROM categories ORDER BY name');
    res.json(result.rows);
  } catch (err) {
    console.error('Error al actualizar categoría:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.delete('/api/categories/:id', async (req, res) => {
  const { id } = req.params;

  try {
    await db.query('DELETE FROM categories WHERE id = $1', [id]);
    const result = await db.query('SELECT id, name FROM categories ORDER BY name');
    res.json(result.rows);
  } catch (err) {
    console.error('Error al eliminar categoría:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(process.env.PORT, '0.0.0.0', () => {
  console.log(`Backend listening on port ${process.env.PORT}`);
});
