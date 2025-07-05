
const db = require('../database/dbPool');

exports.getExpenses = async (req, res) => {
  try {
    const result = await db.query(
      `SELECT 
        expenses.*, 
        months.name AS month_name, 
        years.value AS year_value, 
        categories.name AS category_name
      FROM expenses
      JOIN months ON expenses.month_id = months.id
      JOIN years ON expenses.year_id = years.id
      JOIN categories ON expenses.category_id = categories.id
      ORDER BY years.value, months.id`
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error al obtener gastos:', err);
    res.status(500).json({ error: 'Error al obtener gastos' });
  }
};

exports.createExpense = async (req, res) => {
  const { name, cost, month_id, year_id, category_id } = req.body;
  try {
    await db.query(
      'INSERT INTO expenses (name, cost, month_id, year_id, category_id) VALUES ($1, $2, $3, $4, $5)',
      [name, cost, month_id, year_id, category_id]
    );

    const result = await db.query(
      `SELECT 
        expenses.*, 
        months.name AS month_name, 
        years.value AS year_value, 
        categories.name AS category_name
      FROM expenses
      JOIN months ON expenses.month_id = months.id
      JOIN years ON expenses.year_id = years.id
      JOIN categories ON expenses.category_id = categories.id
      ORDER BY years.value, months.id`
    );

    res.json(result.rows);
  } catch (err) {
    console.error('Error al agregar gasto:', err);
    res.status(500).json({ error: 'Error al agregar gasto' });
  }
};

exports.updateExpense = async (req, res) => {
  const { id } = req.params;
  const { name, cost, month_id, year_id, category_id } = req.body;
  try {
    await db.query(
      'UPDATE expenses SET name=$1, cost=$2, month_id=$3, year_id=$4, category_id=$5 WHERE id=$6',
      [name, cost, month_id, year_id, category_id, id]
    );

    const result = await db.query(
      `SELECT 
        expenses.*, 
        months.name AS month_name, 
        years.value AS year_value, 
        categories.name AS category_name
      FROM expenses
      JOIN months ON expenses.month_id = months.id
      JOIN years ON expenses.year_id = years.id
      JOIN categories ON expenses.category_id = categories.id
      ORDER BY years.value, months.id`
    );

    res.json(result.rows);
  } catch (err) {
    console.error('Error al actualizar gasto:', err);
    res.status(500).json({ error: 'Error al actualizar gasto' });
  }
};

exports.deleteExpense = async (req, res) => {
  const { id } = req.params;
  try {
    await db.query('DELETE FROM expenses WHERE id=$1', [id]);

    const result = await db.query(
      `SELECT 
        expenses.*, 
        months.name AS month_name, 
        years.value AS year_value, 
        categories.name AS category_name
      FROM expenses
      JOIN months ON expenses.month_id = months.id
      JOIN years ON expenses.year_id = years.id
      JOIN categories ON expenses.category_id = categories.id
      ORDER BY years.value, months.id`
    );

    res.json(result.rows);
  } catch (err) {
    console.error('Error al eliminar gasto:', err);
    res.status(500).json({ error: 'Error al eliminar gasto' });
  }
};
