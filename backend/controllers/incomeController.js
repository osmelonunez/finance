const db = require('../database/dbPool');

// Obtener todos los ingresos
exports.getIncomes = async (req, res) => {
  try {
    const result = await db.query(
      `SELECT incomes.*, months.name AS month_name, years.value AS year_value
       FROM incomes
       JOIN months ON incomes.month_id = months.id
       JOIN years ON incomes.year_id = years.id
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
    const username = req.user.username;

    await db.query(
      `INSERT INTO incomes (
        name, amount, month_id, year_id,
        created_by_user_id, created_by_username,
        last_modified_by_user_id, last_modified_by_username
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
      [
        name,
        amount,
        month_id,
        year_id,
        userId,
        username,
        userId,
        username
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
    const username = req.user.username;

    await db.query(
      `UPDATE incomes
       SET name=$1, amount=$2, month_id=$3, year_id=$4,
           last_modified_by_user_id=$5, last_modified_by_username=$6
       WHERE id=$7`,
      [
        name,
        amount,
        month_id,
        year_id,
        userId,
        username,
        id
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
