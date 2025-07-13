// routes/alert.js

const express = require('express');
const router = express.Router();
const alertController = require('../controllers/alertController');
const { authenticateToken } = require('../middleware/authMiddleware');

// POST   /api/alerts/
router.post('/', authenticateToken, alertController.createAlert);

// GET    /api/alerts/
router.get('/', authenticateToken, alertController.getUserAlerts);

// PATCH  /api/alerts/:id/resolve
router.patch('/:id/resolve', authenticateToken, alertController.resolveAlert);

// GET    /api/alerts/record/:record_id
router.get('/record/:record_id', authenticateToken, alertController.getAlertsByRecord);

module.exports = router;
