export default function InfoModal({ record, onClose }) {
  if (!record) return null;

  // Opcional: Traduce source a label más bonito
  const sourceLabels = {
    current_month: 'Current month',
    general_savings: 'General savings'
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-lg p-6 w-80">
        <h3 className="text-lg font-semibold mb-2 text-gray-700">Info</h3>
        <div className="space-y-2 text-gray-700 text-base">
          <div>
            <b>Created by:</b> {record.created_by_username || record.created_by_user_id || 'N/A'}
          </div>
          <div>
            <b>Created at:</b> {record.created_at ? new Date(record.created_at).toLocaleString() : 'N/A'}
          </div>
          <div>
            <b>Last modified by:</b> {record.last_modified_by_username || record.last_modified_by_user_id || 'N/A'}
          </div>
          <div>
            <b>Last updated:</b> {record.updated_at ? new Date(record.updated_at).toLocaleString() : 'N/A'}
          </div>
          {/* SOLO para expenses que tengan source */}
          {record.source && (
            <div>
              <b>Source:</b> {sourceLabels[record.source] || record.source}
            </div>
          )}
        </div>
        <button
          onClick={onClose}
          className="mt-4 px-4 py-2 rounded bg-green-100 border border-green-300 text-green-700 hover:bg-green-200"
        >
          Close
        </button>
      </div>
    </div>
  );
}
