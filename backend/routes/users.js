const express = require('express');
const router = express.Router();
const { authenticateToken, authorizeRoles } = require('../middleware/authMiddleware');
const usersController = require('../controllers/usersController');

// Obtener todos los usuarios (solo admin)
router.get(
  '/',
  authenticateToken,
  authorizeRoles('admin'),
  usersController.getAllUsers
);

// Actualizar estado activo/inactivo de usuario (solo admin)
router.put(
  '/:id/status',
  authenticateToken,
  authorizeRoles('admin'),
  usersController.updateUserStatus
);

// Eliminar usuario (solo admin)
router.delete(
  '/:id',
  authenticateToken,
  authorizeRoles('admin'),
  usersController.deleteUser
);

module.exports = router;