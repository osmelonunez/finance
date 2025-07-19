const jwt = require('jsonwebtoken');

// Verifica que el token sea válido
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Token requerido' });

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    //console.log('Payload JWT:', user);
    if (err) return res.status(403).json({ error: 'Token inválido o expirado' });
    req.user = user;
    next();
  });
}

// Verifica que el usuario tenga uno de los roles permitidos
function authorizeRoles(...roles) {
  return (req, res, next) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Acceso denegado: rol no autorizado' });
    }
    next();
  };
}

module.exports = {
  authenticateToken,
  authorizeRoles,
};
