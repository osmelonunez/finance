const db = require('../database/dbPool');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

exports.loginUser = async (req, res) => {
  const { username, password } = req.body;
  try {
    const result = await db.query('SELECT * FROM users WHERE username = $1', [username]);
    const user = result.rows[0];

    if (!user) {
      return res.status(401).json({ error: 'Credenciales inválidas' });
    }

    const match = await bcrypt.compare(password, user.password_hash);
    if (!match) {
      return res.status(401).json({ error: 'Credenciales inválidas' });
    }

    const token = jwt.sign({ userId: user.id, username: user.username }, process.env.JWT_SECRET, {
      expiresIn: '1h'
    });

    res.json({ token });
  } catch (err) {
    console.error('Error en /login:', err);
    res.status(500).json({ error: 'Error en el login' });
  }
};

exports.getMe = async (req, res) => {
  try {
    const result = await db.query('SELECT id, username FROM users WHERE id = $1', [req.user.userId]);
    const user = result.rows[0];
    if (!user) return res.status(404).json({ error: 'Usuario no encontrado' });
    res.json(user);
  } catch (err) {
    console.error('Error en /api/me GET:', err);
    res.status(500).json({ error: 'Error al obtener el usuario' });
  }
};


exports.updateMe = async (req, res) => {
  const { username, password } = req.body;

  try {
    const updates = [];
    const values = [];
    let paramIndex = 1;

    if (username) {
      const exists = await db.query(
        'SELECT id FROM users WHERE username = $1 AND id != $2',
        [username, req.user.userId]
      );
      if (exists.rows.length > 0) {
        return res.status(400).json({ error: 'Ese nombre de usuario ya está en uso' });
      }
      updates.push(`username = $${paramIndex++}`);
      values.push(username);
    }

    if (password) {
      const hashed = await bcrypt.hash(password, 10);
      updates.push(`password_hash = $${paramIndex++}`);
      values.push(hashed);
    }

    if (updates.length === 0) {
      return res.status(400).json({ error: 'Nada para actualizar' });
    }

    values.push(req.user.userId);

    await db.query(
      `UPDATE users SET ${updates.join(', ')}, updated_at = CURRENT_TIMESTAMP WHERE id = $${paramIndex}`,
      values
    );

    res.json({ message: 'Actualización exitosa' });
  } catch (err) {
    console.error('Error en /api/me PUT:', err);
    res.status(500).json({ error: 'Error al actualizar el usuario' });
  }
};
