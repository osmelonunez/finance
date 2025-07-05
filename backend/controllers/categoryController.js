const db = require('../database/dbPool');

exports.getCategories = async (req, res) => {
  try {
    const result = await db.query('SELECT id, name, description FROM categories ORDER BY name');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error al obtener categorías' });
  }
};

exports.createCategory = async (req, res) => {
  const { name, description } = req.body;
  if (!name) {
    return res.status(400).json({ error: 'El nombre es requerido' });
  }

  try {
    const result = await db.query(
      'INSERT INTO categories (name, description) VALUES ($1, $2) RETURNING *',
      [name, description || null]
    );
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error al agregar la categoría' });
  }
};

exports.updateCategory = async (req, res) => {
  const { id } = req.params;
  const { name, description } = req.body;

  try {
    await db.query(
      'UPDATE categories SET name = $1, description = $2 WHERE id = $3',
      [name, description || null, id]
    );
    res.sendStatus(200);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error al actualizar la categoría' });
  }
};

exports.deleteCategory = async (req, res) => {
  const { id } = req.params;

  try {
    const usageCheck = await db.query('SELECT 1 FROM expenses WHERE category_id = $1 LIMIT 1', [id]);
    if (usageCheck.rowCount > 0) {
      return res.status(400).json({ error: 'The category cannot be deleted because it is in use.' });
    }

    await db.query('DELETE FROM categories WHERE id = $1', [id]);
    res.sendStatus(200);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error al eliminar la categoría' });
  }
};