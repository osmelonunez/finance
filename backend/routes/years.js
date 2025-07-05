const express = require('express');
const router = express.Router();
const yearsController = require('../controllers/yearsController');

router.get('/', yearsController.getYears);
router.post('/', yearsController.createYear);
router.delete('/:id', yearsController.deleteYear);

module.exports = router;