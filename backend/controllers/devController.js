const fs = require('fs');
const path = require('path');
const db = require('../database/dbPool');

// Ejecuta el script SQL para insertar datos de prueba
exports.seedData = async (req, res) => {
  try {
    const sql = fs.readFileSync(path.join(__dirname, '../scripts/seed_dev.sql'), 'utf-8');
    await db.query(sql);
    res.json({ success: true, message: 'Datos de prueba insertados.' });
  } catch (err) {
    console.error('Error ejecutando script de seed:', err);
    res.status(500).json({ error: 'Error insertando datos de prueba' });
  }
};

// Ejecuta el script SQL para eliminar los datos de prueba
exports.cleanData = async (req, res) => {
  try {
    const sql = fs.readFileSync(path.join(__dirname, '../scripts/clean_dev.sql'), 'utf-8');
    await db.query(sql);
    res.json({ success: true, message: 'Datos de prueba eliminados.' });
  } catch (err) {
    console.error('Error ejecutando script de clean:', err);
    res.status(500).json({ error: 'Error eliminando datos de prueba' });
  }
};
