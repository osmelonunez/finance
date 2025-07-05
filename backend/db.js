const { initializeDatabase } = require('./database/init');

initializeDatabase()
  .then(() => console.log("✅ Base de datos inicializada correctamente."))
  .catch(err => {
    console.error("❌ Error inicializando la base de datos:", err);
    process.exit(1);
  });
