const express = require('express');
const router = express.Router();
const expensesController = require('../controllers/expensesController');
const { authenticateToken } = require('../middleware/authMiddleware');

// Todas las rutas están protegidas con token JWT
// No se filtra por usuario ni por rol

router.get('/', authenticateToken, expensesController.getExpenses);
router.post('/', authenticateToken, expensesController.createExpense);
router.put('/:id', authenticateToken, expensesController.updateExpense);
router.delete('/:id', authenticateToken, expensesController.deleteExpense);

module.exports = router;
