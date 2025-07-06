const express = require('express');
const router = express.Router();
const registerController = require('../controllers/registerController');

// Ruta pública: permite a cualquier usuario registrarse

router.post('/', registerController.registerUser);

module.exports = router;
