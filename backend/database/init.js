const bcrypt = require('bcrypt');
const { Client } = require('pg');
const pool = require('./dbPool');
require('dotenv').config();

const adminUsername = process.env.ADMIN_USERNAME;
const adminEmail = process.env.ADMIN_EMAIL;
const adminPassword = process.env.ADMIN_PASSWORD;
const RETRY_DELAY_MS = 10000; // 7 segundos
const { runMigrations } = require('./migrations/migrate');

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
    CREATE TABLE IF NOT EXISTS migrations (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255) UNIQUE NOT NULL,
      run_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);

  console.log("✅ Tabla 'migrations' verificada/creada.");

  await client.query(`
    CREATE TABLE IF NOT EXISTS roles (
      id SERIAL PRIMARY KEY,
      name VARCHAR(50) UNIQUE NOT NULL
    );
  `);

  await client.query(`
    INSERT INTO roles (name)
    VALUES ('admin'), ('editor'), ('viewer')
    ON CONFLICT (name) DO NOTHING;
  `);

  console.log("✅ Tabla 'roles' verificada/creada.");

  await client.query(`
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      username VARCHAR(255) UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      role_id INTEGER REFERENCES roles(id) DEFAULT 3,
      active BOOLEAN NOT NULL DEFAULT FALSE,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);

  console.log("✅ Tabla 'users' verificada/creada.");

  await client.query(`
    CREATE TABLE IF NOT EXISTS alerts (
      id SERIAL PRIMARY KEY,
      created_by INTEGER REFERENCES users(id) NOT NULL,
      record_id INTEGER,
      record_type VARCHAR(30),
      message TEXT NOT NULL,
      type VARCHAR(50),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      resolved BOOLEAN NOT NULL DEFAULT FALSE,
      resolved_by INTEGER REFERENCES users(id),
      resolved_at TIMESTAMP,
      due_date TIMESTAMP
    );
  `);
  
  console.log("✅ Tabla 'alerts' verificada/creada.");

  await client.query(`
    CREATE TABLE IF NOT EXISTS emails (
      id SERIAL PRIMARY KEY,
      user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      email VARCHAR(255) UNIQUE NOT NULL,
      is_primary BOOLEAN DEFAULT false,
      notifications_enabled BOOLEAN DEFAULT true,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);

  console.log("✅ Tabla 'emails' verificada/creada.");
  
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
      year_id INT NOT NULL REFERENCES years(id),
      created_by_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
      last_modified_by_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);

  console.log("✅ Tabla 'incomes' verificada/creada.");

  await client.query(`
    CREATE TABLE IF NOT EXISTS savings (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      amount NUMERIC(10, 2) NOT NULL,
      month_id INT NOT NULL REFERENCES months(id),
      year_id INT NOT NULL REFERENCES years(id),
      created_by_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
      last_modified_by_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'source_type') THEN
            CREATE TYPE source_type AS ENUM ('current_month', 'general_savings');
        END IF;
    END$$;
  `);

  await client.query(`
    CREATE TABLE IF NOT EXISTS expenses (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      cost NUMERIC(10, 2) NOT NULL,
      month_id INT NOT NULL REFERENCES months(id),
      year_id INT NOT NULL REFERENCES years(id),
      category_id INTEGER REFERENCES categories(id) ON DELETE RESTRICT,
      source source_type NOT NULL DEFAULT 'current_month',
      created_by_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
      last_modified_by_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);

  console.log("✅ Tabla 'expenses' verificada/creada.");

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
      ('Suscripciones', 'Netflix, iCloud, Spotify, Amazon Prime')
    ON CONFLICT DO NOTHING;
  `);

  console.log("✅ Categorías insertadas en la tabla 'categories'.");

  await client.query(`
  INSERT INTO months (id, name)
  VALUES
    (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
    (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
    (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
  ON CONFLICT DO NOTHING;
  `);

  console.log("✅ Meses insertados en la tabla 'months'.");

  await client.query(`
    INSERT INTO years (value)
    VALUES (2025)
    ON CONFLICT DO NOTHING;
  `);

  console.log("✅ Años insertados en la tabla 'years'.");

  await client.query(`
    CREATE OR REPLACE FUNCTION update_timestamp()
    RETURNS TRIGGER AS $$
    BEGIN
      NEW.updated_at = CURRENT_TIMESTAMP;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
  `);

  // Para tabla emails
  await client.query(`
    DROP TRIGGER IF EXISTS set_timestamp ON emails;
  `);
  await client.query(`
    CREATE TRIGGER set_timestamp
    BEFORE UPDATE ON emails
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();
  `);

  // Para tabla alerts
  await client.query(`
    DROP TRIGGER IF EXISTS set_timestamp ON alerts;
  `);
  await client.query(`
    CREATE TRIGGER set_timestamp
    BEFORE UPDATE ON alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();
  `);

  // Para tabla users
  await client.query(`
    DROP TRIGGER IF EXISTS set_user_timestamp ON users;
  `);
  await client.query(`
    CREATE TRIGGER set_user_timestamp
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();
  `);

  // Para tabla incomes
  await client.query(`
    DROP TRIGGER IF EXISTS set_incomes_timestamp ON incomes;
  `);
  await client.query(`
    CREATE TRIGGER set_incomes_timestamp
    BEFORE UPDATE ON incomes
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();
  `);

  // Para tabla expenses
  await client.query(`
    DROP TRIGGER IF EXISTS set_expenses_timestamp ON expenses;
  `);
  await client.query(`
    CREATE TRIGGER set_expenses_timestamp
    BEFORE UPDATE ON expenses
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();
  `);

  // Para tabla savings
  await client.query(`
    DROP TRIGGER IF EXISTS set_savings_timestamp ON savings;
  `);
  await client.query(`
    CREATE TRIGGER set_savings_timestamp
    BEFORE UPDATE ON savings
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();
  `);

  console.log("✅ Trigger 'set_timestamp' creado/verificado.");

  if (adminUsername && adminEmail && adminPassword) {
    const passwordHash = await bcrypt.hash(adminPassword, 10);
  
    await client.query(`
      INSERT INTO users (username, password_hash, role_id, active)
      VALUES ($1, $2, 1, TRUE)
      ON CONFLICT (username) DO NOTHING;
    `, [adminUsername, passwordHash]);
    
    const res = await client.query(`SELECT id FROM users WHERE username = $1`, [adminUsername]);
    const adminId = res.rows[0]?.id;
    
    if (adminId) {
      await client.query(`
        INSERT INTO emails (user_id, email, is_primary)
        VALUES ($1, $2, true)
        ON CONFLICT (email) DO NOTHING;
      `, [adminId, adminEmail]);
    }
  
    console.log(`✅ Usuario administrador "${adminUsername}" creado/verificado con rol admin.`);
  } else {
    console.warn("⚠️  Variables ADMIN_USERNAME, ADMIN_EMAIL o ADMIN_PASSWORD no definidas. No se creó el usuario admin.");
  }

  await runMigrations();

  await client.end();

}

module.exports = { initializeDatabase };
