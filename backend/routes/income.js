const express = require('express');
const router = express.Router();
const incomeController = require('../controllers/incomeController');
const { authenticateToken } = require('../middleware/authMiddleware');

// Todas las rutas están protegidas con token JWT
// No hay restricciones por rol, cualquier usuario autenticado puede acceder

router.get('/', authenticateToken, incomeController.getIncomes);
router.post('/', authenticateToken, incomeController.createIncome);
router.put('/:id', authenticateToken, incomeController.updateIncome);
router.delete('/:id', authenticateToken, incomeController.deleteIncome);

module.exports = router;
