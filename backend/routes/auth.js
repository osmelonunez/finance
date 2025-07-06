const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');
const { authenticateToken } = require('../middleware/authMiddleware');

// 📌 Ruta pública para login
router.post('/login', authController.loginUser);

// 📌 Rutas protegidas para ver y actualizar el perfil personal
router.get('/me', authenticateToken, authController.getMe);
router.put('/me', authenticateToken, authController.updateMe);

module.exports = router;
