const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');

router.post('/login', authController.loginUser);

const authenticateToken = require('../middleware/authMiddleware');

router.get('/me', authenticateToken, authController.getMe);

router.put('/me', authenticateToken, authController.updateMe);

module.exports = router;