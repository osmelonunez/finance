import { useState, useEffect } from "react";

export default function AlertsManagerPage() {
  // Simulación de alertas (en real, fetch desde tu API)
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    // Aquí deberías hacer fetch a tu endpoint GET /api/alerts
    // Ejemplo demo:
    setTimeout(() => {
      setAlerts([
        { id: 1, message: "Monthly report available", resolved: false, date: "2024-07-11" },
        { id: 2, message: "System update scheduled", resolved: true, date: "2024-07-13" },
      ]);
      setLoading(false);
    }, 500);
  }, []);

  // Handler para crear una alerta nueva (ejemplo demo)
  const handleCreateAlert = (e) => {
    e.preventDefault();
    if (!message.trim()) return;
    const newAlert = {
      id: Date.now(),
      message,
      resolved: false,
      date: new Date().toISOString().slice(0, 10)
    };
    setAlerts([newAlert, ...alerts]);
    setMessage("");
  };

  // Handler para marcar como resuelta
  const handleResolve = (id) => {
    setAlerts(alerts =>
      alerts.map(alert =>
        alert.id === id ? { ...alert, resolved: true } : alert
      )
    );
  };

  return (
    <div className="max-w-xl mx-auto mt-10 bg-white rounded shadow p-6">
      <h1 className="text-xl font-bold mb-4">Manage Alerts</h1>

      {/* Crear alerta */}
      <form onSubmit={handleCreateAlert} className="flex mb-6 gap-2">
        <input
          type="text"
          placeholder="New alert message"
          className="flex-1 border px-3 py-2 rounded"
          value={message}
          onChange={e => setMessage(e.target.value)}
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
        >
          Create
        </button>
      </form>

      {/* Lista de alertas */}
      {loading ? (
        <div className="text-gray-500 text-center py-4">Loading alerts...</div>
      ) : alerts.length === 0 ? (
        <div className="text-gray-400 text-center py-6">No alerts found.</div>
      ) : (
        <ul>
          {alerts.map(alert => (
            <li
              key={alert.id}
              className={`mb-2 px-4 py-2 rounded border flex justify-between items-center ${alert.resolved ? "bg-gray-100 text-gray-400" : "bg-yellow-50 border-yellow-200"}`}
            >
              <div>
                <span className="font-medium">{alert.message}</span>
                <span className="block text-xs text-gray-400">{alert.date}</span>
              </div>
              {!alert.resolved && (
                <button
                  onClick={() => handleResolve(alert.id)}
                  className="bg-green-500 text-white text-xs px-3 py-1 rounded ml-3 hover:bg-green-600"
                >
                  Mark as resolved
                </button>
              )}
              {alert.resolved && (
                <span className="text-green-600 font-bold text-xs">Resolved</span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
