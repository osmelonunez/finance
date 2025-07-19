const fs = require("fs");
const path = require("path");
const db = require("../dbPool");

const MIGRATIONS_DIR = __dirname; // Carpeta actual: /backend/database/migrations

async function ensureMigrationsTable() {
  await db.query(`
    CREATE TABLE IF NOT EXISTS migrations (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255) UNIQUE NOT NULL,
      run_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);
}

async function getAppliedMigrations() {
  const res = await db.query('SELECT name FROM migrations');
  return new Set(res.rows.map(row => row.name));
}

async function applyMigration(fileName, sql) {
  console.log(`🔄 Applying migration: ${fileName}`);
  await db.query(sql);
  await db.query(
    'INSERT INTO migrations (name) VALUES ($1)',
    [fileName]
  );
  console.log(`✅ Migration applied: ${fileName}`);
}

async function runMigrations() {
  await ensureMigrationsTable();
  const applied = await getAppliedMigrations();

  // Filtra solo archivos .sql y ordena por nombre
  const migrationFiles = fs.readdirSync(MIGRATIONS_DIR)
    .filter(f => f.endsWith('.sql'))
    .sort();

  for (const file of migrationFiles) {
    if (!applied.has(file)) {
      const sql = fs.readFileSync(path.join(MIGRATIONS_DIR, file), "utf-8");
      await applyMigration(file, sql);
    } else {
      console.log(`🟢 Already applied: ${file}`);
    }
  }

  console.log("🚀 All migrations done.");
}

// Permite correr desde línea de comandos (node migrate.js)
if (require.main === module) {
  runMigrations()
    .then(() => process.exit(0))
    .catch(err => {
      console.error("❌ Migration error:", err);
      process.exit(1);
    });
}

module.exports = { runMigrations };
