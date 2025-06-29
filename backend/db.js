const { Pool, Client } = require('pg');
require('dotenv').config();

const RETRY_DELAY_MS = 10000; // 7 segundos

async function waitAndRetry(fn, label = 'acción', retries = 20) {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
            const result = await fn();
      console.log(`✔️  ${label} exitosa en intento ${attempt}`);
      return result;
    } catch (err) {
      console.error(`❌ Fallo en ${label} (intento ${attempt}/${retries}):`, err.message);
      if (attempt === retries) throw err;
      await new Promise(res => setTimeout(res, RETRY_DELAY_MS));
    }
  }
}

const dbName = process.env.DB_NAME;

async function initializeDatabase() {
  console.log("🔍 Comprobando existencia de la base de datos...");

  async function connectAdminClient() {
    const client = new Client({
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      host: process.env.DB_HOST,
      port: process.env.DB_PORT,
      database: 'postgres',
    });
    await client.connect();
    return client;
  }

  const adminClient = await waitAndRetry(connectAdminClient, 'conexión inicial');

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
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      username VARCHAR(255) UNIQUE NOT NULL,
      email VARCHAR(255) UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);
  console.log("✅ Tabla 'users' verificada/creada.");

  await client.query(`
    CREATE TABLE IF NOT EXISTS months (
      id INT PRIMARY KEY CHECK (id BETWEEN 1 AND 12),
      name VARCHAR(20) NOT NULL
    );
  `);
  console.log("✅ Tabla 'months' verificada/creada.");

  await client.query(`
    CREATE TABLE IF NOT EXISTS years (
      id SERIAL PRIMARY KEY,
      value INT NOT NULL UNIQUE
    );
  `);
  console.log("✅ Tabla 'years' verificada/creada.");

  await client.query(`
    CREATE TABLE IF NOT EXISTS incomes (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      amount NUMERIC(10, 2) NOT NULL,
      month_id INT NOT NULL REFERENCES months(id),
      year_id INT NOT NULL REFERENCES years(id)
    );
  `);
  console.log("✅ Tabla 'incomes' verificada/creada.");

  await client.query(`
    CREATE TABLE IF NOT EXISTS savings (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255),
      amount NUMERIC(10, 2) NOT NULL,
      month_id INT NOT NULL REFERENCES months(id),
      year_id INT NOT NULL REFERENCES years(id)
    );
  `);
  console.log("✅ Tabla 'savings' verificada/creada.");

  await client.query(`
    CREATE TABLE IF NOT EXISTS categories (
      id SERIAL PRIMARY KEY,
      name TEXT NOT NULL UNIQUE,
      description TEXT
    );
  `);
  console.log("✅ Tabla 'categories' verificada/creada.");

  await client.query(`
    CREATE TABLE IF NOT EXISTS expenses (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      cost NUMERIC(10, 2) NOT NULL,
      month_id INT NOT NULL REFERENCES months(id),
      year_id INT NOT NULL REFERENCES years(id),
      category_id INTEGER REFERENCES categories(id) ON DELETE RESTRICT
    );
  `);
  console.log("✅ Tabla 'expenses' verificada/creada.");

  console.log("🏁 Inicialización de base de datos finalizada.");

  await client.query(`
    INSERT INTO categories (name, description)
    VALUES 
      ('Gastos Básicos', 'Alquiler o hipoteca, comunidad, servicios (luz, agua, fibra/móvil, gas), seguros de vida y de hogar'),
      ('Hogar', 'Reformas, compras para el hogar'),
      ('Alimentación', 'Supermercado, cafés y snacks'),
      ('Ocio', 'Salidas, viajes, cine, conciertos'),
      ('Transporte', 'Seguro del coche, mantenimiento, combustible, tarjeta de transporte'),
      ('Personal', 'Ropa, calzado, peluquería, barbería'),
      ('Deporte', 'Gimnasio, yoga, natación'),
      ('Salud', 'Seguros de salud, medicamentos'),
      ('Suscripciones', 'Netflix, iCloud, Spotify, Amazon Prime'),
      ('Finanzas y deudas', 'Pagos aplazados, préstamos')
    ON CONFLICT DO NOTHING;
  `);

  await client.query(`
  INSERT INTO months (id, name)
  VALUES
    (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
    (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
    (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
  ON CONFLICT DO NOTHING;
  `);

  await client.query(`
    INSERT INTO years (value)
      SELECT generate_series(2025, 2026)
    ON CONFLICT DO NOTHING;
  `);

  console.log("✅ Categorías insertadas en la tabla 'categories'.");

  await client.end();

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
