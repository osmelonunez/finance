const express = require('express');
const router = express.Router();
const { authenticateToken, authorizeRoles } = require('../middleware/authMiddleware');
const usersController = require('../controllers/usersController');

router.get(
  '/',
  authenticateToken,
  authorizeRoles('admin'), // 👈 solo admin puede acceder
  usersController.getAllUsers
);

module.exports = router;
