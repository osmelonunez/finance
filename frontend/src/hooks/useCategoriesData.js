import { useEffect, useState } from 'react';

export default function useCategoriesData(endpoint = '/api/categories') {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(endpoint);
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
  }, [endpoint]);

  return { categories, loading };
}