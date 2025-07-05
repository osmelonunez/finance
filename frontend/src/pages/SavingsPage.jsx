import RecordsPageTemplate from '../components/records/RecordsPageTemplate';

export default function SavingsPage() {
  return (
    <RecordsPageTemplate
      type="savings"
      title="Savings"
      endpoint="/api/savings"
      field="amount"
      color="green"
      storageKey="savings"
      hasCategory={false}
    />
  );
}
