// controllers/alertController.js

const db = require('../database/dbPool');

// Crear una alerta
exports.createAlert = async (req, res) => {
  const { record_id, record_type, message, type, due_date } = req.body;
  const created_by = req.user.userId;

  try {
    const result = await db.query(
      `INSERT INTO alerts (created_by, record_id, record_type, message, type, due_date)
       VALUES ($1, $2, $3, $4, $5, $6)
       RETURNING *`,
      [created_by, record_id, record_type, message, type, due_date]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error('Error creating alert:', err);
    res.status(500).json({ error: 'Error creating alert' });
  }
};

// Obtener todas las alertas activas (visibles para todos)
exports.getUserAlerts = async (req, res) => {
  try {
    const result = await db.query(
      `SELECT 
          a.*, 
          u1.username AS created_by_name, 
          u2.username AS resolved_by_name
        FROM alerts a
        LEFT JOIN users u1 ON a.created_by = u1.id
        LEFT JOIN users u2 ON a.resolved_by = u2.id
        ORDER BY a.resolved ASC, a.due_date ASC NULLS LAST, a.created_at DESC`
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error fetching alerts:', err);
    res.status(500).json({ error: 'Error fetching alerts' });
  }
};

// Marcar una alerta como resuelta
exports.resolveAlert = async (req, res) => {
  const resolved_by = req.user.userId;
  const alert_id = req.params.id;

  try {
    const result = await db.query(
      `UPDATE alerts
       SET resolved = true,
           resolved_by = $1,
           resolved_at = CURRENT_TIMESTAMP
       WHERE id = $2
       RETURNING *`,
      [resolved_by, alert_id]
    );
    if (result.rowCount === 0) {
      return res.status(404).json({ error: 'Alert not found' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error('Error resolving alert:', err);
    res.status(500).json({ error: 'Error resolving alert' });
  }
};

// Obtener alertas asociadas a un registro
exports.getAlertsByRecord = async (req, res) => {
  const user_id = req.user.userId;
  const { record_id } = req.params;

  try {
    const result = await db.query(
      `SELECT * FROM alerts
       WHERE user_id = $1 AND record_id = $2
       ORDER BY created_at DESC`,
      [user_id, record_id]
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error fetching alerts by record:', err);
    res.status(500).json({ error: 'Error fetching alerts by record' });
  }
};
