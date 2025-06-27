const { Pool, Client } = require('pg');
require('dotenv').config();

const dbName = 'finance';

async function initializeDatabase() {
  console.log("🔍 Comprobando existencia de la base de datos...");

  const adminClient = new Client({
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    database: 'postgres',
  });

  await adminClient.connect();

  const res = await adminClient.query('SELECT 1 FROM pg_database WHERE datname = $1', [dbName]);
  if (res.rowCount === 0) {
    await adminClient.query(`CREATE DATABASE ${dbName}`);
    console.log(`✅ Base de datos "${dbName}" creada correctamente.`);
  } else {
    console.log(`ℹ️  La base de datos "${dbName}" ya existe.`);
  }
  await adminClient.end();

  console.log("🔍 Conectando a la base de datos para verificar/crear tablas...");

  const client = new Client({
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    database: dbName,
  });

  await client.connect();

  await client.query(`
    CREATE TABLE IF NOT EXISTS expenses (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      cost NUMERIC(10, 2) NOT NULL,
      month INT NOT NULL,
      year INT NOT NULL,
      category_id INTEGER REFERENCES categories(id) ON DELETE RESTRICT
    );
  `);
  console.log("✅ Tabla 'expenses' verificada/creada.");

  await client.query(`
    CREATE TABLE IF NOT EXISTS incomes (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      amount NUMERIC(10, 2) NOT NULL,
      month INT NOT NULL,
      year INT NOT NULL
    );
  `);
  console.log("✅ Tabla 'incomes' verificada/creada.");

  await client.query(`
    CREATE TABLE IF NOT EXISTS categories (
      id SERIAL PRIMARY KEY,
      name TEXT NOT NULL UNIQUE
    );
  `);
  console.log("✅ Tabla 'categories' verificada/creada.");

  await client.end();
  console.log("🏁 Inicialización de base de datos finalizada.");
}

// Ejecutar inicialización antes de exportar el pool
initializeDatabase().catch(err => {
  console.error("❌ Error inicializando la base de datos:", err);
  process.exit(1);
});

const pool = new Pool({
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: dbName,
});

module.exports = pool;
