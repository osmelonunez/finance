import RecordsPageTemplate from '../components/records/RecordsPageTemplate';

export default function IncomesPage() {
  return (
    <RecordsPageTemplate
      type="incomes"
      title="Incomes"
      endpoint="/api/incomes"
      field="amount"
      color="green"
      storageKey="incomes"
      hasCategory={false}
    />
  );
}
