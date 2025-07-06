const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const cron = require('node-cron');

// Aquí podrías guardar la configuración en un archivo JSON o en la base de datos
const SCHEDULE_PATH = path.join(__dirname, '../config/backup_schedule.json');

// Backup inmediato: ejecuta pg_dump (ajusta el comando según tu base de datos y ruta)
async function createBackupNow (req, res) {
  try {
    // Ruta del backup (puedes ajustar la carpeta si quieres)
    const backupPath = path.join(__dirname, `../backups/backup_${Date.now()}.sql`);
    const command = `PGPASSWORD='${process.env.DB_PASSWORD}' pg_dump -U ${process.env.DB_USER} -h ${process.env.DB_HOST} ${process.env.DB_NAME} > "${backupPath}"`;

    exec(command, { env: process.env }, (error, stdout, stderr) => {
      if (error) {
        console.error('Error creating backup:', error, stderr);
        return res.status(500).json({ error: 'Error creating backup', details: stderr });
      }
      res.json({ success: true, path: backupPath });
    });
  } catch (err) {
    console.error('Backup error:', err);
    res.status(500).json({ error: 'Error creating backup' });
  }
};

// Guarda la configuración de programación (días y hora)
async function saveSchedule(req, res) {
  try {
    const { days, time } = req.body;
    const config = { days, time };
    fs.writeFileSync(SCHEDULE_PATH, JSON.stringify(config, null, 2));
    res.json({ success: true });
  } catch (err) {
    console.error('Error saving backup schedule:', err);
    res.status(500).json({ error: 'Error saving schedule' });
  }
};

const scheduleLogDir = path.join(__dirname, '../logs');
if (!fs.existsSync(scheduleLogDir)) fs.mkdirSync(scheduleLogDir, { recursive: true });
const scheduleLogPath = path.join(scheduleLogDir, 'backupschedule.log');

// Leer la programación actual
function getSchedule(req, res) {
  try {
    if (!fs.existsSync(SCHEDULE_PATH)) {
      const msg = `[${new Date().toISOString()}] getSchedule: No schedule config found.\n`;
      fs.appendFileSync(scheduleLogPath, msg);
      return res.json({});
    }
    const config = JSON.parse(fs.readFileSync(SCHEDULE_PATH));
    const msg = `[${new Date().toISOString()}] getSchedule: Read schedule config: ${JSON.stringify(config)}\n`;
    fs.appendFileSync(scheduleLogPath, msg);
    res.json(config);
  } catch (err) {
    const msg = `[${new Date().toISOString()}] getSchedule: Error reading schedule: ${err.message}\n`;
    fs.appendFileSync(scheduleLogPath, msg);
    res.status(500).json({ error: 'Error reading schedule' });
  }
}

function loadScheduleConfig() {
  try {
    const configPath = path.join(__dirname, '../config/backup_schedule.json');
    if (!fs.existsSync(configPath)) {
      const msg = `[${new Date().toISOString()}] loadScheduleConfig: No schedule config found.\n`;
      fs.appendFileSync(scheduleLogPath, msg);
      return null;
    }
    const config = JSON.parse(fs.readFileSync(configPath));
    const msg = `[${new Date().toISOString()}] loadScheduleConfig: Loaded schedule config: ${JSON.stringify(config)}\n`;
    fs.appendFileSync(scheduleLogPath, msg);
    return config;
  } catch (err) {
    const msg = `[${new Date().toISOString()}] loadScheduleConfig: Error loading schedule: ${err.message}\n`;
    fs.appendFileSync(scheduleLogPath, msg);
    console.error('Error loading backup schedule:', err);
    return null;
  }
}

// Convierte días ['Mon', 'Wed', ...] y hora '22:00' a expresión cron
function getCronExpression(days, time) {
  // Días a números cron: Sun=0, Mon=1, ..., Sat=6
  const dayMap = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
  const daysNumbers = days.map(d => dayMap[d]).join(',');
  const [hour, minute] = time.split(':');
  return `${minute} ${hour} * * ${daysNumbers}`;
}

function scheduleBackupJob() {
  const config = loadScheduleConfig();

  // Log para depuración
  const scheduleLogDir = path.join(__dirname, '../logs');
  if (!fs.existsSync(scheduleLogDir)) fs.mkdirSync(scheduleLogDir, { recursive: true });
  const scheduleLogPath = path.join(scheduleLogDir, 'backup.log');

  if (!config || !config.days || !config.time) {
    const msg = `[${new Date().toISOString()}] No schedule config found. Backup cron not scheduled.\n`;
    fs.appendFileSync(scheduleLogPath, msg);
    console.log(msg);
    return;
  }
  const cronExp = getCronExpression(config.days, config.time);

  // Log programación
  const msg = `[${new Date().toISOString()}] Scheduling backup at ${config.time} on ${config.days.join(', ')} (cron: ${cronExp})\n`;
  fs.appendFileSync(scheduleLogPath, msg);
  console.log(msg);

  cron.schedule(cronExp, () => {
    const backupDir = path.join(__dirname, '../backups');
    if (!fs.existsSync(backupDir)) fs.mkdirSync(backupDir, { recursive: true });
    const backupPath = path.join(backupDir, `backup_${Date.now()}.sql`);
    const command = `PGPASSWORD='${process.env.DB_PASSWORD}' pg_dump -U ${process.env.DB_USER} -h ${process.env.DB_HOST} ${process.env.DB_NAME} > "${backupPath}"`;

    // Log de backup
    const backupLogPath = path.join(scheduleLogDir, 'backup.log');

    exec(command, { env: process.env }, (error, stdout, stderr) => {
      if (error) {
        const errMessage = `[${new Date().toISOString()}] Scheduled backup failed: ${stderr}\n`;
        fs.appendFileSync(backupLogPath, errMessage);
        console.error('Scheduled backup failed:', error, stderr);
      } else {
        const logMessage = `[${new Date().toISOString()}] Scheduled backup created: ${backupPath}\n`;
        fs.appendFileSync(backupLogPath, logMessage);
        console.log('Scheduled backup created:', backupPath);
      }
    });
  });
}


module.exports = {
  createBackupNow,
  saveSchedule,
  getSchedule,
  scheduleBackupJob,
};