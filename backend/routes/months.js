const express = require('express');
const router = express.Router();
const monthsController = require('../controllers/monthsController');

router.get('/', monthsController.getMonths);

module.exports = router;