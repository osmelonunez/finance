const db = require('../database/dbPool');

// Obtener todos los usuarios con su rol
exports.getAllUsers = async (req, res) => {
  try {
    const result = await db.query(
      `SELECT users.id, users.username, users.role_id, roles.name AS role, users.active
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

// Actualizar estado activo/inactivo de un usuario
exports.updateUserStatus = async (req, res) => {
  const { id } = req.params;
  const { active } = req.body;
  try {
    await db.query('UPDATE users SET active = $1 WHERE id = $2', [active, id]);
    res.json({ success: true });
  } catch (err) {
    console.error('Error al actualizar estado del usuario:', err);
    res.status(500).json({ error: 'Error actualizando el estado del usuario' });
  }
};

// Eliminar usuario (opcional)
exports.deleteUser = async (req, res) => {
  const { id } = req.params;
  try {
    await db.query('DELETE FROM users WHERE id = $1', [id]);
    res.json({ success: true });
  } catch (err) {
    console.error('Error al eliminar usuario:', err);
    res.status(500).json({ error: 'Error eliminando el usuario' });
  }
};

// Actualizar role de un usuario
exports.updateUserRole = async (req, res) => {
  const { id } = req.params;
  const { role_id } = req.body;
  try {
    await db.query('UPDATE users SET role_id = $1 WHERE id = $2', [role_id, id]);
    res.json({ success: true });
  } catch (err) {
    console.error('Error al actualizar el rol:', err);
    res.status(500).json({ error: 'Error al actualizar el rol del usuario' });
  }
};
