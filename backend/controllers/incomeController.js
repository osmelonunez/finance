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

// Crear ingreso sin asociarlo a un usuario específico
exports.createIncome = async (req, res) => {
  const { name, amount, month_id, year_id } = req.body;

  try {
    await db.query(
      'INSERT INTO incomes (name, amount, month_id, year_id) VALUES ($1, $2, $3, $4)',
      [name, amount, month_id, year_id]
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

// Actualizar cualquier ingreso por ID
exports.updateIncome = async (req, res) => {
  const { id } = req.params;
  const { name, amount, month_id, year_id } = req.body;

  try {
    await db.query(
      'UPDATE incomes SET name=$1, amount=$2, month_id=$3, year_id=$4 WHERE id=$5',
      [name, amount, month_id, year_id, id]
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

// Eliminar cualquier ingreso por ID
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
