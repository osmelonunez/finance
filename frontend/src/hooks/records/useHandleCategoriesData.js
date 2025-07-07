import { useEffect, useState } from 'react';
import useAuthToken from '../useAuthToken';

export default function useCategoriesData(endpoint = '/api/categories') {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const token = useAuthToken();

  useEffect(() => {
    if (!token) return;

    const load = async () => {
      try {
        const res = await fetch(endpoint, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (res.ok) {
          const data = await res.json();
          setCategories(data);
        } else {
          console.error('Error al obtener categorías:', res.statusText);
        }
      } catch (err) {
        console.error('Error al obtener categorías:', err);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [endpoint, token]);

  return { categories, loading };
}
