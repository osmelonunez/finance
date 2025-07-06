const db = require('../database/dbPool');

exports.getAllRoles = async (req, res) => {
  try {
    const result = await db.query('SELECT id, name FROM roles ORDER BY id');
    res.json(result.rows);
  } catch (err) {
    console.error('Error al obtener roles:', err);
    res.status(500).json({ error: 'Error al obtener roles' });
  }
};
