import { useEffect, useState } from 'react';
import useAuthToken from '../useAuthToken';

export default function useRecordsData(endpoint) {
  const [records, setRecords] = useState([]);
  const [months, setMonths] = useState([]);
  const [years, setYears] = useState([]);
  const [loading, setLoading] = useState(true);

  const token = useAuthToken();

  useEffect(() => {
    async function fetchData() {
      if (!token) return;

      setLoading(true);
      try {
        const [recordsRes, monthsRes, yearsRes] = await Promise.all([
          fetch(endpoint, {
            headers: { Authorization: `Bearer ${token}` }
          }),
          fetch('/api/months', {
            headers: { Authorization: `Bearer ${token}` }
          }),
          fetch('/api/years', {
            headers: { Authorization: `Bearer ${token}` }
          }),
        ]);

        if (!recordsRes.ok || !monthsRes.ok || !yearsRes.ok) {
          throw new Error('Unauthorized or failed to fetch data.');
        }

        const [recordsData, monthsData, yearsData] = await Promise.all([
          recordsRes.json(),
          monthsRes.json(),
          yearsRes.json(),
        ]);

        setRecords(recordsData);
        setMonths(monthsData);
        setYears(yearsData);
      } catch (err) {
        console.error('Error loading data:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [endpoint, token]);

  return { records, setRecords, months, years, loading };
}
