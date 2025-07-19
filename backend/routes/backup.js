const express = require('express');
const router = express.Router();
const backupController = require('../controllers/backupController');
// Puedes proteger con authenticateToken y authorizeRoles('admin') si lo deseas

router.post('/now', backupController.createBackupNow);
router.post('/schedule', backupController.saveSchedule);
router.get('/schedule', backupController.getSchedule);

module.exports = router;