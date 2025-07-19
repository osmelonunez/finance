const db = require('../database/dbPool');

// Devuelve el nombre del registro asociado, dado el tipo y el ID
async function getRecordName(type, id) {
  if (!type || !id) return null;
  let table = '';

  if (type === 'expenses') table = 'expenses';
  else if (type === 'incomes') table = 'incomes';
  else if (type === 'savings') table = 'savings';
  else return null;

  try {
    const result = await db.query(`SELECT name FROM ${table} WHERE id = $1`, [id]);
    return result.rows[0]?.name || null;
  } catch (e) {
    console.error(`Error fetching ${type} name:`, e);
    return null;
  }
}

// Handler para obtener todas las alertas
exports.getAlerts = async (req, res) => {
  try {
    // Consulta todas las alertas
    const result = await db.query('SELECT * FROM alerts ORDER BY created_at DESC');
    const alerts = Array.isArray(result.rows) ? result.rows : [];

    // Enriquecer cada alerta con el nombre si aplica
    const alertsWithNames = await Promise.all(
      alerts.map(async alert => {
        if (alert.record_type && alert.record_id) {
          alert.record_name = await getRecordName(alert.record_type, alert.record_id);
        }
        return alert;
      })
    );

    res.json(alertsWithNames); // Siempre un array
  } catch (err) {
    console.error("Error en getAlerts:", err);
    res.status(500).json({ error: "Error fetching alerts" });
  }
};

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

// Editar alerta (mensaje o fecha)
exports.updateAlert = async (req, res) => {
  const alertId = req.params.id;
  const { message, due_date } = req.body;
  try {
    const result = await db.query(
      `UPDATE alerts
       SET message = COALESCE($1, message),
           due_date = COALESCE($2, due_date),
           updated_at = CURRENT_TIMESTAMP
       WHERE id = $3
       RETURNING *`,
      [message, due_date, alertId]
    );
    if (result.rowCount === 0) {
      return res.status(404).json({ error: 'Alert not found' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error('Error updating alert:', err);
    res.status(500).json({ error: 'Error updating alert' });
  }
};

exports.deleteAlert = async (req, res) => {
  try {
    const alertId = req.params.id;
    await db.query('DELETE FROM alerts WHERE id = $1', [alertId]);
    res.json({ success: true });
  } catch (err) {
    console.error("Error deleting alert:", err);
    res.status(500).json({ error: "Error deleting alert" });
  }
};