const db = require('../database/dbPool');

// Obtener todos los ingresos
exports.getIncomes = async (req, res) => {
  try {
    const result = await db.query(
      `SELECT 
         incomes.*, 
         months.name AS month_name, 
         years.value AS year_value,
         u1.username AS created_by_username,
         u2.username AS last_modified_by_username
       FROM incomes
       JOIN months ON incomes.month_id = months.id
       JOIN years ON incomes.year_id = years.id
       LEFT JOIN users u1 ON incomes.created_by_user_id = u1.id
       LEFT JOIN users u2 ON incomes.last_modified_by_user_id = u2.id
       ORDER BY years.value, months.id`
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error al obtener ingresos:', err);
    res.status(500).json({ error: 'Error al obtener ingresos' });
  }
};

// Crear ingreso y asociar usuario
exports.createIncome = async (req, res) => {
  const { name, amount, month_id, year_id } = req.body;

  try {
    const userId = req.user.userId;

    await db.query(
      `INSERT INTO incomes (
        name, amount, month_id, year_id,
        created_by_user_id,
        last_modified_by_user_id
      ) VALUES ($1, $2, $3, $4, $5, $6)`,
      [
        name,
        amount,
        month_id,
        year_id,
        userId,
        userId
      ]
    );

    const result = await db.query(
      `SELECT incomes.*, months.name AS month_name, years.value AS year_value
       FROM incomes
       JOIN months ON incomes.month_id = months.id
       JOIN years ON incomes.year_id = years.id
       ORDER BY years.value, months.id`
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error al agregar ingreso:', err);
    res.status(500).json({ error: 'Error al agregar ingreso' });
  }
};

// Actualizar cualquier ingreso por ID y asociar usuario modificador
exports.updateIncome = async (req, res) => {
  const { id } = req.params;
  const { name, amount, month_id, year_id } = req.body;

  try {
    const userId = req.user.userId;

    await db.query(
      `UPDATE incomes
       SET name=$1, amount=$2, month_id=$3, year_id=$4,
           last_modified_by_user_id=$5
       WHERE id=$6`,
      [
        name,
        amount,
        month_id,
        year_id,
        userId,
        id
      ]
    );

    const result = await db.query(
      `SELECT 
         incomes.*, 
         months.name AS month_name, 
         years.value AS year_value,
         u1.username AS created_by_username,
         u2.username AS last_modified_by_username
       FROM incomes
       JOIN months ON incomes.month_id = months.id
       JOIN years ON incomes.year_id = years.id
       LEFT JOIN users u1 ON incomes.created_by_user_id = u1.id
       LEFT JOIN users u2 ON incomes.last_modified_by_user_id = u2.id
       ORDER BY years.value, months.id`
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error al actualizar ingreso:', err);
    res.status(500).json({ error: 'Error al actualizar ingreso' });
  }
};

// Eliminar cualquier ingreso por ID (sin cambio)
exports.deleteIncome = async (req, res) => {
  const { id } = req.params;

  try {
    await db.query('DELETE FROM incomes WHERE id = $1', [id]);

    const result = await db.query(
      `SELECT incomes.*, months.name AS month_name, years.value AS year_value
       FROM incomes
       JOIN months ON incomes.month_id = months.id
       JOIN years ON incomes.year_id = years.id
       ORDER BY years.value, months.id`
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error al eliminar ingreso:', err);
    res.status(500).json({ error: 'Error al eliminar ingreso' });
  }
};
