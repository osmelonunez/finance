const db = require('../database/dbPool');

exports.getAllUsers = async (req, res) => {
  try {
    const result = await db.query(
      `SELECT users.id, users.username, roles.name AS role
       FROM users
       JOIN roles ON users.role_id = roles.id
       ORDER BY users.id`
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error al obtener usuarios:', err);
    res.status(500).json({ error: 'Error al obtener usuarios' });
  }
};
