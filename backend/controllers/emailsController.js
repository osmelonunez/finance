const db = require('../database/dbPool');

exports.getEmails = async (req, res) => {
  try {
    const result = await db.query(
      'SELECT * FROM emails WHERE user_id = $1 ORDER BY is_primary DESC, created_at ASC',
      [req.user.userId]
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error al obtener correos:', err);
    res.status(500).json({ error: 'Error al obtener correos' });
  }
};

exports.createEmail = async (req, res) => {
  const { email, is_primary, notifications_enabled } = req.body;

  if (!email) return res.status(400).json({ error: 'Email requerido' });

  try {
    const existing = await db.query('SELECT * FROM emails WHERE email = $1', [email]);
    if (existing.rows.length > 0)
      return res.status(400).json({ error: 'Ese correo ya está registrado' });

    await db.query(
      'INSERT INTO emails (user_id, email, is_primary, notifications_enabled) VALUES ($1, $2, $3, $4)',
      [req.user.userId, email, is_primary || false, notifications_enabled || true]
    );

    const result = await db.query(
      'SELECT * FROM emails WHERE user_id = $1 ORDER BY created_at',
      [req.user.userId]
    );
    res.status(201).json(result.rows);
  } catch (err) {
    console.error('Error al agregar correo:', err);
    res.status(500).json({ error: 'Error al agregar correo' });
  }
};

exports.updateEmail = async (req, res) => {
  const { email, is_primary, notifications_enabled } = req.body;
  const emailId = req.params.id;

  try {
    const match = await db.query(
      'SELECT * FROM emails WHERE id = $1 AND user_id = $2',
      [emailId, req.user.userId]
    );
    if (match.rows.length === 0)
      return res.status(404).json({ error: 'Correo no encontrado' });

    if (is_primary) {
      await db.query(
        'UPDATE emails SET is_primary = false WHERE user_id = $1',
        [req.user.userId]
      );
    }

    await db.query(
      'UPDATE emails SET is_primary = $1, notifications_enabled = $2 WHERE id = $3',
      [!!is_primary, !!notifications_enabled, emailId]
    );

    if (email) {
      await db.query('UPDATE emails SET email = $1 WHERE id = $2', [email, emailId]);
    }

    const result = await db.query(
      'SELECT * FROM emails WHERE user_id = $1 ORDER BY created_at',
      [req.user.userId]
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error al actualizar correo:', err);
    res.status(500).json({ error: 'Error al actualizar correo' });
  }
};

exports.deleteEmail = async (req, res) => {
  const emailId = req.params.id;

  try {
    const match = await db.query(
      'SELECT * FROM emails WHERE id = $1 AND user_id = $2',
      [emailId, req.user.userId]
    );
    if (match.rows.length === 0)
      return res.status(404).json({ error: 'Correo no encontrado' });

    await db.query('DELETE FROM emails WHERE id = $1', [emailId]);

    const result = await db.query(
      'SELECT * FROM emails WHERE user_id = $1 ORDER BY created_at',
      [req.user.userId]
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error al eliminar correo:', err);
    res.status(500).json({ error: 'Error al eliminar correo' });
  }
};