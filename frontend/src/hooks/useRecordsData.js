import { useEffect, useState } from 'react';

export default function useRecordsData(endpoint) {
  const [records, setRecords] = useState([]);
  const [months, setMonths] = useState([]);
  const [years, setYears] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const [recordsRes, monthsRes, yearsRes] = await Promise.all([
          fetch(endpoint),
          fetch('/api/months'),
          fetch('/api/years'),
        ]);

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
  }, [endpoint]);

  return { records, setRecords, months, years, loading };
}
