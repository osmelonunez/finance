const express = require('express');
const cors = require('cors');
const db = require('./db');
require('dotenv').config();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Token requerido' });

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: 'Token inválido o expirado' });
    req.user = user;
    next();
  });
}

const app = express();
app.use(cors());
app.use(express.json());

app.get('/api/expenses', async (req, res) => {
  try {
    const result = await db.query(`
      SELECT 
        expenses.*, 
        months.name AS month_name, 
        years.value AS year_value, 
        categories.name AS category_name
      FROM expenses
      JOIN months ON expenses.month_id = months.id
      JOIN years ON expenses.year_id = years.id
      JOIN categories ON expenses.category_id = categories.id
      ORDER BY years.value, months.id
    `);
    res.json(result.rows);
  } catch (err) {
    console.error('Error al obtener gastos:', err);
    res.status(500).json({ error: 'Error al obtener gastos' });
  }
});

app.post('/api/expenses', async (req, res) => {
  const { name, cost, month_id, year_id, category_id } = req.body;
  try {
    await db.query(
      'INSERT INTO expenses (name, cost, month_id, year_id, category_id) VALUES ($1, $2, $3, $4, $5)',
      [name, cost, month_id, year_id, category_id]
    );

    const result = await db.query(`
      SELECT 
        expenses.*, 
        months.name AS month_name, 
        years.value AS year_value, 
        categories.name AS category_name
      FROM expenses
      JOIN months ON expenses.month_id = months.id
      JOIN years ON expenses.year_id = years.id
      JOIN categories ON expenses.category_id = categories.id
      ORDER BY years.value, months.id
    `);

    res.json(result.rows);
  } catch (err) {
    console.error('Error al agregar gasto:', err);
    res.status(500).json({ error: 'Error al agregar gasto' });
  }
});

app.put('/api/expenses/:id', async (req, res) => {
  const { id } = req.params;
  const { name, cost, month_id, year_id, category_id } = req.body;
  try {
    await db.query(
      'UPDATE expenses SET name=$1, cost=$2, month_id=$3, year_id=$4, category_id=$5 WHERE id=$6',
      [name, cost, month_id, year_id, category_id, id]
    );

    const result = await db.query(`
      SELECT 
        expenses.*, 
        months.name AS month_name, 
        years.value AS year_value, 
        categories.name AS category_name
      FROM expenses
      JOIN months ON expenses.month_id = months.id
      JOIN years ON expenses.year_id = years.id
      JOIN categories ON expenses.category_id = categories.id
      ORDER BY years.value, months.id
    `);

    res.json(result.rows);
  } catch (err) {
    console.error('Error al actualizar gasto:', err);
    res.status(500).json({ error: 'Error al actualizar gasto' });
  }
});

app.delete('/api/expenses/:id', async (req, res) => {
  const { id } = req.params;
  try {
    await db.query('DELETE FROM expenses WHERE id=$1', [id]);

    const result = await db.query(`
      SELECT 
        expenses.*, 
        months.name AS month_name, 
        years.value AS year_value, 
        categories.name AS category_name
      FROM expenses
      JOIN months ON expenses.month_id = months.id
      JOIN years ON expenses.year_id = years.id
      JOIN categories ON expenses.category_id = categories.id
      ORDER BY years.value, months.id
    `);

    res.json(result.rows);
  } catch (err) {
    console.error('Error al eliminar gasto:', err);
    res.status(500).json({ error: 'Error al eliminar gasto' });
  }
});

app.post('/api/incomes', async (req, res) => {
  const { name, amount, month_id, year_id } = req.body;
  try {
    await db.query(
      'INSERT INTO incomes (name, amount, month_id, year_id) VALUES ($1, $2, $3, $4)',
      [name, amount, month_id, year_id]
    );
    const result = await db.query(`
      SELECT incomes.*, months.name AS month_name, years.value AS year_value
      FROM incomes
      JOIN months ON incomes.month_id = months.id
      JOIN years ON incomes.year_id = years.id
      ORDER BY years.value, months.id
    `);
    res.json(result.rows);
  } catch (err) {
    console.error('Error al agregar ingreso:', err);
    res.status(500).json({ error: 'Error al agregar ingreso' });
  }
});

app.put('/api/incomes/:id', async (req, res) => {
  const { id } = req.params;
  const { name, amount, month_id, year_id } = req.body;
  try {
    await db.query(
      'UPDATE incomes SET name=$1, amount=$2, month_id=$3, year_id=$4 WHERE id=$5',
      [name, amount, month_id, year_id, id]
    );
    const result = await db.query(`
      SELECT incomes.*, months.name AS month_name, years.value AS year_value
      FROM incomes
      JOIN months ON incomes.month_id = months.id
      JOIN years ON incomes.year_id = years.id
      ORDER BY years.value, months.id
    `);
    res.json(result.rows);
  } catch (err) {
    console.error('Error al actualizar ingreso:', err);
    res.status(500).json({ error: 'Error al actualizar ingreso' });
  }
});

app.delete('/api/incomes/:id', async (req, res) => {
  const { id } = req.params;
  try {
    await db.query('DELETE FROM incomes WHERE id=$1', [id]);
    const result = await db.query(`
      SELECT incomes.*, months.name AS month_name, years.value AS year_value
      FROM incomes
      JOIN months ON incomes.month_id = months.id
      JOIN years ON incomes.year_id = years.id
      ORDER BY years.value, months.id
    `);
    res.json(result.rows);
  } catch (err) {
    console.error('Error al eliminar ingreso:', err);
    res.status(500).json({ error: 'Error al eliminar ingreso' });
  }
});

app.get('/api/incomes', async (req, res) => {
  try {
    const result = await db.query(`
      SELECT incomes.*, months.name AS month_name, years.value AS year_value
      FROM incomes
      JOIN months ON incomes.month_id = months.id
      JOIN years ON incomes.year_id = years.id
      ORDER BY years.value, months.id
    `);
    res.json(result.rows);
  } catch (err) {
    console.error('Error al obtener ingresos:', err);
    res.status(500).json({ error: 'Error al obtener ingresos' });
  }
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
    const result = await db.query(`
      SELECT 
        savings.*, 
        months.name AS month_name, 
        years.value AS year_value
      FROM savings
      JOIN months ON savings.month_id = months.id
      JOIN years ON savings.year_id = years.id
      ORDER BY year_value, month_id
    `);

    res.json(result.rows);
  } catch (err) {
    console.error('Error al obtener ahorros:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Agregar nuevo ahorro
app.post('/api/savings', async (req, res) => {
  const { name, amount, month_id, year_id } = req.body;

  if (!name?.trim() || !amount || !month_id || !year_id) {
    return res.status(400).json({ error: 'Datos incompletos' });
  }

  try {
    await db.query(
      'INSERT INTO savings (name, amount, month_id, year_id) VALUES ($1, $2, $3, $4)',
      [name.trim(), amount, month_id, year_id]
    );

    const result = await db.query(`
      SELECT savings.*, months.name AS month_name, years.value AS year_value
      FROM savings
      JOIN months ON savings.month_id = months.id
      JOIN years ON savings.year_id = years.id
      ORDER BY year_value, month_id
    `);

    res.json(result.rows);
  } catch (err) {
    console.error('Error al agregar ahorro:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Editar ahorro
app.put('/api/savings/:id', async (req, res) => {
  const { id } = req.params;
  const { name, amount, month_id, year_id } = req.body;

  try {
    await db.query(
      'UPDATE savings SET name = $1, amount = $2, month_id = $3, year_id = $4 WHERE id = $5',
      [name.trim(), amount, month_id, year_id, id]
    );

    const result = await db.query(`
      SELECT savings.*, months.name AS month_name, years.value AS year_value
      FROM savings
      JOIN months ON savings.month_id = months.id
      JOIN years ON savings.year_id = years.id
      ORDER BY year_value, month_id
    `);

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

    const result = await db.query(`
      SELECT savings.*, months.name AS month_name, years.value AS year_value
      FROM savings
      JOIN months ON savings.month_id = months.id
      JOIN years ON savings.year_id = years.id
      ORDER BY year_value, month_id
    `);

    res.json(result.rows);
  } catch (err) {
    console.error('Error al eliminar ahorro:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /api/months
app.get('/api/months', async (req, res) => {
  try {
    const result = await db.query('SELECT id, name FROM months ORDER BY id');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error al obtener meses' });
  }
});

// GET /api/years
app.get('/api/years', async (req, res) => {
  try {
    const result = await db.query('SELECT id, value FROM years ORDER BY value');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error al obtener años' });
  }
});

// POST /api/years
app.post('/api/years', async (req, res) => {
  const { value } = req.body;
  if (!value || isNaN(value)) {
    return res.status(400).json({ error: 'Año inválido' });
  }

  try {
    await db.query('INSERT INTO years (value) VALUES ($1) ON CONFLICT DO NOTHING', [value]);
    const result = await db.query('SELECT id, value FROM years ORDER BY value');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error al agregar año' });
  }
});

// DELETE /api/years/:id
app.delete('/api/years/:id', async (req, res) => {
  const { id } = req.params;
  try {
    await db.query('DELETE FROM years WHERE id = $1', [id]);
    const result = await db.query('SELECT id, value FROM years ORDER BY value');
    res.json(result.rows);
  } catch (err) {
    if (err.code === '23503') {
      // foreign key violation
      return res.status(400).json({ error: 'This year is in use and cannot be deleted.' });
    }
    console.error('Error deleting year:', err);
    res.status(500).json({ error: 'Unable to delete year.' });
  }
});


app.listen(process.env.BACKEND_PORT, '0.0.0.0', () => {
  console.log(`Backend listening on port ${process.env.BACKEND_PORT}`);
});

// Registro de usuario que también agrega correo principal en la tabla emails
app.post('/api/register', async (req, res) => {
  const { username, email, password } = req.body;

  if (!username || !email || !password) {
    return res.status(400).json({ error: 'Todos los campos son obligatorios' });
  }

  try {
    const userExists = await db.query('SELECT * FROM users WHERE username = $1', [username]);
    const emailExists = await db.query('SELECT * FROM emails WHERE email = $1', [email]);

    if (userExists.rows.length > 0) {
      return res.status(400).json({ error: 'Ya existe un usuario con ese nombre' });
    }

    if (emailExists.rows.length > 0) {
      return res.status(400).json({ error: 'Ya existe un usuario con ese correo' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    // Crear usuario
    const newUser = await db.query(
      'INSERT INTO users (username, password_hash) VALUES ($1, $2) RETURNING id',
      [username, hashedPassword]
    );

    const userId = newUser.rows[0].id;

    // Agregar email principal
    await db.query(
      'INSERT INTO emails (user_id, email, is_primary, notifications_enabled) VALUES ($1, $2, true, true)',
      [userId, email]
    );

    res.status(201).json({ message: 'Usuario y correo registrados con éxito' });
  } catch (err) {
    console.error('Error en /register:', err);
    res.status(500).json({ error: 'Error en el registro' });
  }
});



app.post('/api/login', async (req, res) => {
  const { username, password } = req.body;
  try {
    const result = await db.query('SELECT * FROM users WHERE username = $1', [username]);
    const user = result.rows[0];

    if (!user) {
      return res.status(401).json({ error: 'Credenciales inválidas' });
    }

    const match = await bcrypt.compare(password, user.password_hash);
    if (!match) {
      return res.status(401).json({ error: 'Credenciales inválidas' });
    }

    const token = jwt.sign({ userId: user.id, username: user.username }, process.env.JWT_SECRET, {
      expiresIn: '1h'
    });

    res.json({ token });
  } catch (err) {
    console.error('Error en /login:', err);
    res.status(500).json({ error: 'Error en el login' });
  }
});

// ENDPOINTS PARA GESTIÓN DE CORREOS

// Obtener todos los correos del usuario autenticado
app.get('/api/emails', authenticateToken, async (req, res) => {
  try {
    const result = await db.query('SELECT * FROM emails WHERE user_id = $1 ORDER BY is_primary DESC, created_at ASC', [req.user.userId]);
    res.json(result.rows);
  } catch (err) {
    console.error('Error al obtener correos:', err);
    res.status(500).json({ error: 'Error al obtener correos' });
  }
});

// Agregar un nuevo correo
app.post('/api/emails', authenticateToken, async (req, res) => {
  const { email, is_primary, notifications_enabled } = req.body;

  if (!email) return res.status(400).json({ error: 'Email requerido' });

  try {
    const existing = await db.query('SELECT * FROM emails WHERE email = $1', [email]);
    if (existing.rows.length > 0) return res.status(400).json({ error: 'Ese correo ya está registrado' });

    await db.query(
      'INSERT INTO emails (user_id, email, is_primary, notifications_enabled) VALUES ($1, $2, $3, $4)',
      [req.user.userId, email, is_primary || false, notifications_enabled || true]
    );

    const result = await db.query('SELECT * FROM emails WHERE user_id = $1 ORDER BY created_at', [req.user.userId]);
    res.status(201).json(result.rows);
  } catch (err) {
    console.error('Error al agregar correo:', err);
    res.status(500).json({ error: 'Error al agregar correo' });
  }
});

// Actualizar propiedades de un correo (is_primary, notifications_enabled)
app.put('/api/emails/:id', authenticateToken, async (req, res) => {
  const { is_primary, notifications_enabled } = req.body;
  const emailId = req.params.id;

  try {
    // Solo permitir modificar correos del propio usuario
    const match = await db.query('SELECT * FROM emails WHERE id = $1 AND user_id = $2', [emailId, req.user.userId]);
    if (match.rows.length === 0) return res.status(404).json({ error: 'Correo no encontrado' });

    if (is_primary) {
      await db.query('UPDATE emails SET is_primary = false WHERE user_id = $1', [req.user.userId]);
    }

    await db.query(
      'UPDATE emails SET is_primary = $1, notifications_enabled = $2 WHERE id = $3',
      [!!is_primary, !!notifications_enabled, emailId]
    );

    const result = await db.query('SELECT * FROM emails WHERE user_id = $1 ORDER BY created_at', [req.user.userId]);
    res.json(result.rows);
  } catch (err) {
    console.error('Error al actualizar correo:', err);
    res.status(500).json({ error: 'Error al actualizar correo' });
  }
});

// Eliminar un correo
app.delete('/api/emails/:id', authenticateToken, async (req, res) => {
  const emailId = req.params.id;

  try {
    const match = await db.query('SELECT * FROM emails WHERE id = $1 AND user_id = $2', [emailId, req.user.userId]);
    if (match.rows.length === 0) return res.status(404).json({ error: 'Correo no encontrado' });

    await db.query('DELETE FROM emails WHERE id = $1', [emailId]);

    const result = await db.query('SELECT * FROM emails WHERE user_id = $1 ORDER BY created_at', [req.user.userId]);
    res.json(result.rows);
  } catch (err) {
    console.error('Error al eliminar correo:', err);
    res.status(500).json({ error: 'Error al eliminar correo' });
  }
});

app.get('/api/me', authenticateToken, async (req, res) => {
  try {
    const result = await db.query('SELECT id, username FROM users WHERE id = $1', [req.user.userId]);
    const user = result.rows[0];
    if (!user) return res.status(404).json({ error: 'Usuario no encontrado' });
    res.json(user);
  } catch (err) {
    console.error('Error en /api/me GET:', err);
    res.status(500).json({ error: 'Error al obtener el usuario' });
  }
});

app.put('/api/me', authenticateToken, async (req, res) => {
  const { username, password } = req.body;

  try {
    const updates = [];
    const values = [];
    let paramIndex = 1;

    if (username) {
      // Validar que no esté en uso por otro usuario
      const exists = await db.query(
        'SELECT id FROM users WHERE username = $1 AND id != $2',
        [username, req.user.userId]
      );
      if (exists.rows.length > 0) {
        return res.status(400).json({ error: 'Ese nombre de usuario ya está en uso' });
      }
      updates.push(`username = $${paramIndex++}`);
      values.push(username);
    }

    if (password) {
      const hashed = await bcrypt.hash(password, 10);
      updates.push(`password_hash = $${paramIndex++}`);
      values.push(hashed);
    }

    if (updates.length === 0) {
      return res.status(400).json({ error: 'Nada para actualizar' });
    }

    values.push(req.user.userId);

    await db.query(
      `UPDATE users SET ${updates.join(', ')}, updated_at = CURRENT_TIMESTAMP WHERE id = $${paramIndex}`,
      values
    );

    res.json({ message: 'Actualización exitosa' });
  } catch (err) {
    console.error('Error en /api/me PUT:', err);
    res.status(500).json({ error: 'Error al actualizar el usuario' });
  }
});