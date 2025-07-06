import { createContext, useContext, useState, useEffect } from 'react';
import jwtDecode from 'jwt-decode';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null); // 👈 user con role y username

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decoded = jwtDecode(token);
        setUser(decoded);
        setIsAuthenticated(true);
      } catch {
        setUser(null);
        setIsAuthenticated(false);
      }
    }
  }, []);

  const login = async (username, password) => {
    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
    
      const data = await res.json();
    
      if (res.ok && data.token) {
        localStorage.setItem('token', data.token);
        const decoded = jwtDecode(data.token);
        setUser(decoded);
        setIsAuthenticated(true);
        return true;
      } else {
        // Si el backend envía un error, lo devolvemos como string
        return data.error || 'Usuario o contraseña incorrectos';
      }
    } catch (err) {
      console.error('Login error:', err);
      return 'Ocurrió un error de red. Intenta de nuevo.';
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
