const express = require('express');
const router = express.Router();
const yearsController = require('../controllers/yearsController');
const { authenticateToken } = require('../middleware/authMiddleware');

// Todas las rutas requieren autenticación, sin importar el rol

// Obtener todos los años
router.get('/', authenticateToken, yearsController.getYears);

// Crear un nuevo año
router.post('/', authenticateToken, yearsController.createYear);

// Eliminar un año
router.delete('/:id', authenticateToken, yearsController.deleteYear);

module.exports = router;
