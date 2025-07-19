const { Pool } = require('pg');
require('dotenv').config();

// Validación de variables de entorno necesarias
const requiredEnv = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME'];
for (const varName of requiredEnv) {
  if (!process.env[varName]) {
    console.error(`❌ FALTA VARIABLE DE ENTORNO: ${varName}`);
    process.exit(1);
  }
}

// Crear instancia del pool de conexiones
const pool = new Pool({
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
});

module.exports = pool;
