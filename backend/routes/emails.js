const express = require('express');
const router = express.Router();
const emailsController = require('../controllers/emailsController');
const authenticateToken = require('../middleware/authMiddleware');

router.get('/', authenticateToken, emailsController.getEmails);
router.post('/', authenticateToken, emailsController.createEmail);
router.put('/:id', authenticateToken, emailsController.updateEmail);
router.delete('/:id', authenticateToken, emailsController.deleteEmail);

module.exports = router;