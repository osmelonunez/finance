import { useState, useEffect } from "react";
import AlertList from "../components/alerts/AlertList";

export default function AlertsManagerPage() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [editAlert, setEditAlert] = useState(null);

  // Traer alertas al montar
  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true);
      try {
        const res = await fetch("/api/alerts", {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        const data = await res.json();
        setAlerts(data);
      } catch (err) {}
      setLoading(false);
    };
    fetchAlerts();
  }, []);

  // Crear o editar alerta
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;
    try {
      if (editAlert) {
        // PATCH para editar
        const res = await fetch(`/api/alerts/${editAlert.id}`, {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            message,
            due_date: dueDate || null
          })
        });
        const updated = await res.json();
        setAlerts(alerts =>
          alerts.map(alert =>
            alert.id === editAlert.id ? updated : alert
          )
        );
        setEditAlert(null);
      } else {
        // POST para crear
        const res = await fetch("/api/alerts", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            message,
            record_id: null,
            type: null,
            due_date: dueDate || null
          })
        });
        const newAlert = await res.json();
        if (newAlert && newAlert.id) {
          setAlerts(prev => [newAlert, ...prev]);
        }
      }
      setMessage("");
      setDueDate("");
    } catch (err) {}
  };

  // Marcar alerta como resuelta
  const handleResolve = async (id) => {
    try {
      const res = await fetch(`/api/alerts/${id}/resolve`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      const updated = await res.json();
      setAlerts(alerts =>
        alerts.map(alert =>
          alert.id === id ? updated : alert
        )
      );
    } catch (err) {}
  };

  // Reactivar alerta
  const handleReactivate = async (id) => {
    try {
      const res = await fetch(`/api/alerts/${id}/resolve`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ resolved: false })
      });
      const updated = await res.json();
      setAlerts(alerts =>
        alerts.map(alert =>
          alert.id === id ? updated : alert
        )
      );
    } catch (err) {}
  };

  // Preparar edición
  const handleEdit = (alert) => {
    setEditAlert(alert);
    setMessage(alert.message);
    setDueDate(alert.due_date ? alert.due_date.slice(0,10) : "");
  };

  // Cancelar edición
  const handleCancelEdit = () => {
    setEditAlert(null);
    setMessage("");
    setDueDate("");
  };

  return (
    <div className="max-w-xl mx-auto mt-10 bg-white rounded shadow p-6">
      <h1 className="text-xl font-bold mb-4">Manage Alerts</h1>
      <form onSubmit={handleSubmit} className="flex flex-col gap-2 mb-6">
        <input
          type="text"
          placeholder="New alert message"
          className="border px-3 py-2 rounded"
          value={message}
          onChange={e => setMessage(e.target.value)}
          required
        />
        <input
          type="date"
          value={dueDate}
          onChange={e => setDueDate(e.target.value)}
          className="border px-3 py-2 rounded"
        />
        <div className="flex gap-2">
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
          >
            {editAlert ? "Update" : "Create"}
          </button>
          {editAlert && (
            <button
              type="button"
              onClick={handleCancelEdit}
              className="bg-gray-300 text-black px-4 py-2 rounded"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
      {loading ? (
        <div className="text-gray-500 text-center py-4">Loading alerts...</div>
      ) : (
        <AlertList
          alerts={alerts}
          onResolve={handleResolve}
          onReactivate={handleReactivate}
          onEdit={handleEdit}
        />
      )}
    </div>
  );
}
