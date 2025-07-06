const express = require('express');
const router = express.Router();
const devController = require('../controllers/devController');

// Estos endpoints normalmente solo los usas en desarrollo, no los expongas en producción
router.post('/seed', devController.seedData);
router.delete('/clean', devController.cleanData);

module.exports = router;
