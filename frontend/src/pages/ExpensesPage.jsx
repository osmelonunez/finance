import RecordsPageTemplate from '../components/records/RecordsPageTemplate';

export default function ExpensesPage() {
  return (
    <RecordsPageTemplate
      type="expenses"
      title="Expenses"
      endpoint="/api/expenses"
      field="cost"
      color="green"
      storageKey="expenses"
      hasCategory={true}
    />
  );
}
