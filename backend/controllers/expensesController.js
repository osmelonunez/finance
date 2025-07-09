const db = require('../database/dbPool');

// Obtener todos los gastos
exports.getExpenses = async (req, res) => {
  try {
    const result = await db.query(`
      SELECT 
        expenses.*, 
        months.name AS month_name, 
        years.value AS year_value, 
        categories.name AS category_name,
        u1.username AS created_by_username,
        u2.username AS last_modified_by_username
      FROM expenses
      JOIN months ON expenses.month_id = months.id
      JOIN years ON expenses.year_id = years.id
      JOIN categories ON expenses.category_id = categories.id
      LEFT JOIN users u1 ON expenses.created_by_user_id = u1.id
      LEFT JOIN users u2 ON expenses.last_modified_by_user_id = u2.id
      ORDER BY years.value, months.id
    `);
    res.json(result.rows);
  } catch (err) {
    console.error('Error al obtener gastos:', err);
    res.status(500).json({ error: 'Error al obtener gastos' });
  }
};

exports.getExpenseSources = async (req, res) => {
  try {
    // Obtener los valores del enum directamente de la base de datos
    const result = await db.query(`
      SELECT unnest(enum_range(NULL::source_type)) AS value
    `);

    // Mapea los valores para mostrar un label más "humano"
    const sources = result.rows.map(row => ({
      value: row.value,
      label: row.value
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase())
    }));

    res.json(sources);
  } catch (err) {
    console.error('Error al obtener sources:', err);
    res.status(500).json({ error: 'Error fetching sources' });
  }
};

exports.createExpense = async (req, res) => {
  const { name, cost, month_id, year_id, category_id, source } = req.body;
  try {
    const userId = req.user.userId;

    await db.query(
      `INSERT INTO expenses (
        name, cost, month_id, year_id, category_id, source,
        created_by_user_id,
        last_modified_by_user_id
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
      [
        name,
        cost,
        month_id,
        year_id,
        category_id,
        source || 'current_month',
        userId,
        userId
      ]
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
};

// Actualizar un gasto por ID
exports.updateExpense = async (req, res) => {
  const { id } = req.params;
  const { name, cost, month_id, year_id, category_id, source } = req.body;
  try {
    const userId = req.user.userId;
    const username = req.user.username;

    await db.query(
      `UPDATE expenses
       SET name=$1, cost=$2, month_id=$3, year_id=$4, category_id=$5, source=$6,
           last_modified_by_user_id=$7, last_modified_by_username=$8
       WHERE id=$9`,
      [
        name,
        cost,
        month_id,
        year_id,
        category_id,
        source || 'current_month',
        userId,
        username,
        id
      ]
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
};

// Eliminar un gasto por ID
exports.deleteExpense = async (req, res) => {
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
};