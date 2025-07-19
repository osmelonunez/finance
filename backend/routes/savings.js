const express = require('express');
const router = express.Router();
const savingsController = require('../controllers/savingsController');
const { authenticateToken } = require('../middleware/authMiddleware');

// Todas las rutas requieren token JWT
// No hay restricción por rol ni filtrado por user_id

router.get('/', authenticateToken, savingsController.getSavings);
router.post('/', authenticateToken, savingsController.createSaving);
router.put('/:id', authenticateToken, savingsController.updateSaving);
router.delete('/:id', authenticateToken, savingsController.deleteSaving);

module.exports = router;
