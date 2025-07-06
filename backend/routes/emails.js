const express = require('express');
const router = express.Router();
const emailsController = require('../controllers/emailsController');
const { authenticateToken } = require('../middleware/authMiddleware');

// Todas las acciones requieren que el usuario esté autenticado,
// pero no se restringe por rol ya que cada usuario opera sobre su propia info.

router.get('/', authenticateToken, emailsController.getEmails);
router.post('/', authenticateToken, emailsController.createEmail);
router.put('/:id', authenticateToken, emailsController.updateEmail);
router.delete('/:id', authenticateToken, emailsController.deleteEmail);

module.exports = router;
