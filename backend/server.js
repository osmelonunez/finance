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

// Obtener todas las categorías
app.get('/api/categories', async (req, res) => {
  try {
    const result = await db.query('SELECT id, name, description FROM categories ORDER BY name');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error al obtener categorías' });
  }
});

// Agregar una nueva categoría
app.post('/api/categories', async (req, res) => {
  const { name, description } = req.body;
  if (!name) {
    return res.status(400).json({ error: 'El nombre es requerido' });
  }

  try {
    const result = await db.query(
      'INSERT INTO categories (name, description) VALUES ($1, $2) RETURNING *',
      [name, description || null]
    );
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error al agregar la categoría' });
  }
});

// Actualizar una categoría
app.put('/api/categories/:id', async (req, res) => {
  const { id } = req.params;
  const { name, description } = req.body;

  try {
    await db.query(
      'UPDATE categories SET name = $1, description = $2 WHERE id = $3',
      [name, description || null, id]
    );
    res.sendStatus(200);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error al actualizar la categoría' });
  }
});

// Eliminar una categoría (verifica si está en uso)
app.delete('/api/categories/:id', async (req, res) => {
  const { id } = req.params;

  try {
    // Verificar si hay gastos asociados a esta categoría
    const usageCheck = await db.query('SELECT 1 FROM expenses WHERE category_id = $1 LIMIT 1', [id]);
    if (usageCheck.rowCount > 0) {
      return res.status(400).json({ error: 'The category cannot be deleted because it is in use.' });
    }

    // Eliminar la categoría si no está en uso
    await db.query('DELETE FROM categories WHERE id = $1', [id]);
    res.sendStatus(200);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error al eliminar la categoría' });
  }
});

// Obtener todos los ahorros
app.get('/api/savings', async (req, res) => {
  try {
    const result = await db.query('SELECT * FROM savings ORDER BY year, month');
    res.json(result.rows);
  } catch (err) {
    console.error('Error al obtener ahorros:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Agregar nuevo ahorro
app.post('/api/savings', async (req, res) => {
  const { name, amount, month, year } = req.body;
  if (!name?.trim() || !amount || !month || !year) {
    return res.status(400).json({ error: 'Datos incompletos' });
  }

  try {
    await db.query(
      'INSERT INTO savings (name, amount, month, year) VALUES ($1, $2, $3, $4)',
      [name.trim(), amount, month, year]
    );
    const result = await db.query('SELECT * FROM savings ORDER BY year, month');
    res.json(result.rows);
  } catch (err) {
    console.error('Error al agregar ahorro:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Editar ahorro
app.put('/api/savings/:id', async (req, res) => {
  const { id } = req.params;
  const { name, amount, month, year } = req.body;

  try {
    await db.query(
      'UPDATE savings SET name = $1, amount = $2, month = $3, year = $4 WHERE id = $5',
      [name.trim(), amount, month, year, id]
    );
    const result = await db.query('SELECT * FROM savings ORDER BY year, month');
    res.json(result.rows);
  } catch (err) {
    console.error('Error al actualizar ahorro:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Eliminar ahorro
app.delete('/api/savings/:id', async (req, res) => {
  const { id } = req.params;

  try {
    await db.query('DELETE FROM savings WHERE id = $1', [id]);
    const result = await db.query('SELECT * FROM savings ORDER BY year, month');
    res.json(result.rows);
  } catch (err) {
    console.error('Error al eliminar ahorro:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(process.env.PORT, '0.0.0.0', () => {
  console.log(`Backend listening on port ${process.env.PORT}`);
});
