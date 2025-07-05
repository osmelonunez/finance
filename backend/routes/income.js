
const express = require('express');
const router = express.Router();
const incomeController = require('../controllers/incomeController');

router.post('/', incomeController.createIncome);
router.put('/:id', incomeController.updateIncome);
router.delete('/:id', incomeController.deleteIncome);
router.get('/', incomeController.getIncomes);
module.exports = router;
