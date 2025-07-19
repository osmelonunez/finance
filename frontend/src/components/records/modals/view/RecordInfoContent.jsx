export default function RecordInfoContent({ record, field, hasCategory }) {
  if (!record) return null;
  return (
    <div className="space-y-2">
      <div>
        <span className="font-semibold">Name:</span> {record.name}
      </div>
        <div>
          <span className="font-semibold">{field.charAt(0).toUpperCase() + field.slice(1)}:</span>{" "}
          {record[field] !== undefined && record[field] !== null
            ? <>
                {parseFloat(record[field]).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                <span className="ml-1">€</span>
              </>
            : ""}
        </div>
      <div>
        <span className="font-semibold">Month:</span> {record.month_name}
      </div>
      <div>
        <span className="font-semibold">Year:</span> {record.year_value}
      </div>
      {hasCategory && (
        <div>
          <span className="font-semibold">Category:</span>{" "}
          {record.category_name || record.category_id}
        </div>
      )}
    {record.source && (
      <div>
        <span className="font-semibold">Source:</span>{" "}
        {record.source === "general_savings" && "General savings"}
        {record.source === "current_month" && "Current month"}
        {record.source !== "general_savings" && record.source !== "current_month" && record.source}
      </div>
    )}

      {/* Igual que tu ejemplo */}
      <div>
        <span className="font-semibold">Created by:</span> {record.created_by_username || record.created_by_user_id || 'N/A'}
        {record.created_at && (
          <span> on {new Date(record.created_at).toLocaleString()}</span>
        )}
      </div>
      <div>
        <span className="font-semibold">Last modified by:</span> {record.last_modified_by_username || record.last_modified_by_user_id || 'N/A'}
        {record.updated_at && (
          <span> on {new Date(record.updated_at).toLocaleString()}</span>
        )}
      </div>
    </div>
  );
}
