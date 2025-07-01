// hooks/useAuthToken.js
import { useState, useEffect } from 'react';

export default function useAuthToken() {
  const [token, setToken] = useState(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    setToken(storedToken);
  }, []);

  return token;
}
