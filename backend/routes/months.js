const express = require('express');
const router = express.Router();
const monthsController = require('../controllers/monthsController');
const { authenticateToken } = require('../middleware/authMiddleware');

// Ruta protegida: obtener lista de meses (estática)

router.get('/', authenticateToken, monthsController.getMonths);

module.exports = router;
