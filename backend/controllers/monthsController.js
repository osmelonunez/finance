const db = require('../database/dbPool');

exports.getMonths = async (req, res) => {
  try {
    const result = await db.query('SELECT id, name FROM months ORDER BY id');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error al obtener meses' });
  }
};
