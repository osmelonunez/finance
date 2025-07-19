const db = require('../database/dbPool');

// Obtener todos los años (autenticado, sin importar el rol)
exports.getYears = async (req, res) => {
  try {
    const result = await db.query('SELECT id, value FROM years ORDER BY value');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error al obtener años' });
  }
};

// Crear un año (solo para admin)
exports.createYear = async (req, res) => {
  const { value } = req.body;
  if (!value || isNaN(value)) {
    return res.status(400).json({ error: 'Año inválido' });
  }

  try {
    await db.query('INSERT INTO years (value) VALUES ($1) ON CONFLICT DO NOTHING', [value]);
    const result = await db.query('SELECT id, value FROM years ORDER BY value');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error al agregar año' });
  }
};

// Eliminar un año (solo para admin)
exports.deleteYear = async (req, res) => {
  const { id } = req.params;
  try {
    await db.query('DELETE FROM years WHERE id = $1', [id]);
    const result = await db.query('SELECT id, value FROM years ORDER BY value');
    res.json(result.rows);
  } catch (err) {
    if (err.code === '23503') {
      return res.status(400).json({ error: 'Este año está en uso y no puede eliminarse.' });
    }
    console.error('Error al eliminar año:', err);
    res.status(500).json({ error: 'Error al eliminar año.' });
  }
};
