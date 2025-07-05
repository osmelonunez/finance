const db = require('../database/dbPool');

exports.getSavings = async (req, res) => {
  try {
    const result = await db.query(
      `SELECT 
        savings.*, 
        months.name AS month_name, 
        years.value AS year_value
      FROM savings
      JOIN months ON savings.month_id = months.id
      JOIN years ON savings.year_id = years.id
      ORDER BY year_value, month_id`
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error al obtener ahorros:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
};

exports.createSaving = async (req, res) => {
  const { name, amount, month_id, year_id } = req.body;

  if (!name?.trim() || !amount || !month_id || !year_id) {
    return res.status(400).json({ error: 'Datos incompletos' });
  }

  try {
    await db.query(
      'INSERT INTO savings (name, amount, month_id, year_id) VALUES ($1, $2, $3, $4)',
      [name.trim(), amount, month_id, year_id]
    );

    const result = await db.query(
      `SELECT savings.*, months.name AS month_name, years.value AS year_value
       FROM savings
       JOIN months ON savings.month_id = months.id
       JOIN years ON savings.year_id = years.id
       ORDER BY year_value, month_id`
    );

    res.json(result.rows);
  } catch (err) {
    console.error('Error al agregar ahorro:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
};

exports.updateSaving = async (req, res) => {
  const { id } = req.params;
  const { name, amount, month_id, year_id } = req.body;

  try {
    await db.query(
      'UPDATE savings SET name = $1, amount = $2, month_id = $3, year_id = $4 WHERE id = $5',
      [name.trim(), amount, month_id, year_id, id]
    );

    const result = await db.query(
      `SELECT savings.*, months.name AS month_name, years.value AS year_value
       FROM savings
       JOIN months ON savings.month_id = months.id
       JOIN years ON savings.year_id = years.id
       ORDER BY year_value, month_id`
    );

    res.json(result.rows);
  } catch (err) {
    console.error('Error al actualizar ahorro:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
};

exports.deleteSaving = async (req, res) => {
  const { id } = req.params;

  try {
    await db.query('DELETE FROM savings WHERE id = $1', [id]);

    const result = await db.query(
      `SELECT savings.*, months.name AS month_name, years.value AS year_value
       FROM savings
       JOIN months ON savings.month_id = months.id
       JOIN years ON savings.year_id = years.id
       ORDER BY year_value, month_id`
    );

    res.json(result.rows);
  } catch (err) {
    console.error('Error al eliminar ahorro:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
};