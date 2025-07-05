const db = require('../database/dbPool');

exports.getYears = async (req, res) => {
  try {
    const result = await db.query('SELECT id, value FROM years ORDER BY value');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error al obtener años' });
  }
};

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

exports.deleteYear = async (req, res) => {
  const { id } = req.params;
  try {
    await db.query('DELETE FROM years WHERE id = $1', [id]);
    const result = await db.query('SELECT id, value FROM years ORDER BY value');
    res.json(result.rows);
  } catch (err) {
    if (err.code === '23503') {
      return res.status(400).json({ error: 'This year is in use and cannot be deleted.' });
    }
    console.error('Error deleting year:', err);
    res.status(500).json({ error: 'Unable to delete year.' });
  }
};