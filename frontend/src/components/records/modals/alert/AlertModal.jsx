import { useState } from "react";
import { Bell } from "lucide-react";
import Modal from "../../../common/Modal";

export default function AlertModal({ record, onClose }) {
  const [message, setMessage] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleConfirm = async () => {
    if (!message.trim()) {
      setError("Message is required.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/alerts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          message,
          record_id: record.id,
          record_type: record.record_type,
          type: null,
          due_date: dueDate || null,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || "Failed to create alert.");
        setLoading(false);
        return;
      }
      onClose();
    } catch (err) {
      setError("Network error");
    }
    setLoading(false);
  };

  if (!record) return null;

  return (
    <Modal
      isOpen={!!record}
      onClose={onClose}
      onConfirm={handleConfirm}
      onCancel={onClose}
      confirmText="Create"
      cancelText="Cancel"
      confirmDisabled={loading}
      loading={loading}
    >
      <div className="p-4 w-full max-w-sm">
        <div className="flex items-center gap-2 mb-4">
          <Bell size={22} className="text-yellow-500" />
          <h3 className="text-lg font-semibold">
            Add Alert for{" "}
            <span className="text-blue-700 font-normal">"{record.name}"</span>
          </h3>
        </div>
        <div className="flex flex-col gap-3">
          <label className="block">
            <span className="text-xs text-gray-500">Message</span>
            <input
              type="text"
              value={message}
              onChange={e => setMessage(e.target.value)}
              placeholder="Alert message"
              className="border px-3 py-2 rounded w-full"
              required
              maxLength={100}
              disabled={loading}
            />
          </label>
          <label className="block">
            <span className="text-xs text-gray-500">Target date (optional)</span>
            <input
              type="date"
              value={dueDate}
              onChange={e => setDueDate(e.target.value)}
              className="border px-3 py-2 rounded w-full"
              disabled={loading}
            />
          </label>
          {error && (
            <div className="text-red-600 text-sm">{error}</div>
          )}
        </div>
      </div>
    </Modal>
  );
}
