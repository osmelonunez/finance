const db = require('../database/dbPool');
const bcrypt = require('bcrypt');

exports.registerUser = async (req, res) => {
  const { username, email, password } = req.body;

  if (!username || !email || !password) {

    return res.status(400).json({ error: 'MISSING_FIELDS' });
  }

  try {
    const userExists = await db.query('SELECT * FROM users WHERE username = $1', [username]);
    const emailExists = await db.query('SELECT * FROM emails WHERE email = $1', [email]);

    if (userExists.rows.length > 0) {
      return res.status(400).json({ error: 'USERNAME_EXISTS' });
    }

    if (emailExists.rows.length > 0) {
      return res.status(400).json({ error: 'EMAIL_EXISTS' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const newUser = await db.query(
      'INSERT INTO users (username, password_hash) VALUES ($1, $2) RETURNING id',
      [username, hashedPassword]
    );

    const userId = newUser.rows[0].id;

    await db.query(
      'INSERT INTO emails (user_id, email, is_primary, notifications_enabled) VALUES ($1, $2, true, true)',
      [userId, email]
    );

    res.status(201).json({ message: 'REGISTER_SUCCESS' });
  } catch (err) {
    console.error('Error en /register:', err);
    res.status(500).json({ error: 'REGISTER_ERROR' });
  }
};
