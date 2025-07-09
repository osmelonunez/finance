const db = require('../database/dbPool');

// Obtener todos los ahorros
exports.getSavings = async (req, res) => {
  try {
    const result = await db.query(
      `SELECT 
        savings.*, 
        months.name AS month_name, 
        years.value AS year_value,
        u1.username AS created_by_username,
        u2.username AS last_modified_by_username
       FROM savings
       JOIN months ON savings.month_id = months.id
       JOIN years ON savings.year_id = years.id
       LEFT JOIN users u1 ON savings.created_by_user_id = u1.id
       LEFT JOIN users u2 ON savings.last_modified_by_user_id = u2.id
       ORDER BY year_value, month_id`
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error al obtener ahorros:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
};

// Crear un nuevo ahorro (saving)
exports.createSaving = async (req, res) => {
  const { name, amount, month_id, year_id } = req.body;

  if (!name?.trim() || !amount || !month_id || !year_id) {
    return res.status(400).json({ error: 'Datos incompletos' });
  }

  try {
    const userId = req.user.userId;

    await db.query(
      `INSERT INTO savings (
        name, amount, month_id, year_id,
        created_by_user_id,
        last_modified_by_user_id
      ) VALUES ($1, $2, $3, $4, $5, $6)`,
      [
        name.trim(),
        amount,
        month_id,
        year_id,
        userId,
        userId
      ]
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

// Actualizar un ahorro
exports.updateSaving = async (req, res) => {
  const { id } = req.params;
  const { name, amount, month_id, year_id } = req.body;

  try {
    const userId = req.user.userId;

    await db.query(
      `UPDATE savings
       SET name = $1, amount = $2, month_id = $3, year_id = $4,
           last_modified_by_user_id = $5
       WHERE id = $6`,
      [
        name.trim(),
        amount,
        month_id,
        year_id,
        userId,
        id
      ]
    );

    const result = await db.query(
      `SELECT 
         savings.*, 
         months.name AS month_name, 
         years.value AS year_value,
         u1.username AS created_by_username,
         u2.username AS last_modified_by_username
       FROM savings
       JOIN months ON savings.month_id = months.id
       JOIN years ON savings.year_id = years.id
       LEFT JOIN users u1 ON savings.created_by_user_id = u1.id
       LEFT JOIN users u2 ON savings.last_modified_by_user_id = u2.id
       ORDER BY year_value, month_id`
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error al actualizar ahorro:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
};

// Eliminar un ahorro (sin cambios)
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
