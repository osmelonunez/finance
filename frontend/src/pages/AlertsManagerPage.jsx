import { useState, useEffect, useRef } from "react";
import AlertList from "../components/alerts/AlertList";
import { Plus, Check } from "lucide-react";

export default function AlertsManagerPage() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [editAlert, setEditAlert] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const formRef = useRef();

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;
    try {
      if (editAlert) {
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
      setShowForm(false);
    } catch (err) {}
  };

    const handleEdit = (alert) => {
      if (editAlert && editAlert.id === alert.id) {
        // Si ya está en edición, al darle otra vez cierra la edición
        handleCancelEdit();
      } else {
        setEditAlert(alert);
        setMessage(alert.message);
        setDueDate(alert.due_date ? alert.due_date.slice(0,10) : "");
        setShowForm(true);
      }
    };

  const handleCancelEdit = () => {
    setEditAlert(null);
    setMessage("");
    setDueDate("");
    setShowForm(false);
  };

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

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this alert?")) return;
    try {
      await fetch(`/api/alerts/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setAlerts(alerts => alerts.filter(alert => alert.id !== id));
    } catch (err) {}
  };

  const handlePlusClick = () => {
    if (editAlert) {
      handleCancelEdit();
    } else {
      setShowForm((prev) => !prev);
      if (showForm) {
        setMessage("");
        setDueDate("");
      }
    }
  };

  const handleCheckClick = () => {
    if (formRef.current) {
      formRef.current.requestSubmit();
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-10 bg-white rounded shadow p-6 relative">
      <h1 className="text-xl font-bold mb-4">Manage Alerts</h1>
      {/* Botón agregar y check alineado a la IZQUIERDA debajo del título */}
      <div className="w-full flex justify-start mb-6">
        <button
          onClick={handlePlusClick}
          type="button"
          title={showForm || editAlert ? "Cancel" : "Add alert"}
          className={`
            flex items-center justify-center
            border-2
            ${showForm || editAlert ? "border-yellow-500 text-yellow-500" : "border-green-500 text-green-600"}
            rounded-full
            bg-white
            hover:bg-green-50
            transition-colors duration-150
            focus:outline-none
          `}
          style={{ width: 20, height: 20 }}
        >
          <Plus size={16} strokeWidth={2.2} />
        </button>
        {(showForm || editAlert) && (
          <button
            type="button"
            onClick={handleCheckClick}
            className="ml-2 p-0 rounded-full text-green-600 border-none bg-transparent hover:text-green-700"
            title="Save"
            style={{ width: 18, height: 18 }}
          >
            <Check size={20} />
          </button>
        )}
      </div>

      {(showForm || editAlert) && (
        <form
          ref={formRef}
          onSubmit={handleSubmit}
          className="flex flex-col gap-2 mb-6 mt-4"
        >
          <input
            type="text"
            placeholder="New alert message"
            className="border px-3 py-2 rounded"
            value={message}
            onChange={e => setMessage(e.target.value)}
            required
            autoFocus
          />
          <input
            type="date"
            value={dueDate}
            onChange={e => setDueDate(e.target.value)}
            className="border px-3 py-2 rounded"
          />
        </form>
      )}

      {loading ? (
        <div className="text-gray-500 text-center py-4">Loading alerts...</div>
      ) : (
        <AlertList
          alerts={alerts}
          onResolve={handleResolve}
          onReactivate={handleReactivate}
          onEdit={handleEdit}
          onDelete={handleDelete}
          editAlert={editAlert}
        />
      )}
    </div>
  );
}
