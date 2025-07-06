const express = require('express');
const router = express.Router();
const { authenticateToken, authorizeRoles } = require('../middleware/authMiddleware');
const rolesController = require('../controllers/rolesController');

router.get(
  '/',
  authenticateToken,
  authorizeRoles('admin'), // Solo admin puede ver los roles
  rolesController.getAllRoles
);

module.exports = router;
