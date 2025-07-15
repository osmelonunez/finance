// useHandleDelete.js

export default function useHandleDelete({
  endpoint,
  setRecords,
  showNotification,
  token,
  afterSuccess
}) {
  return async function handleDelete(record) {
    if (!record || !record.id) {
      showNotification && showNotification("No record to delete.", "error");
      return false;
    }

    try {
      const response = await fetch(`${endpoint}/${record.id}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const errorMsg = await response.text();
        console.error("Error al eliminar:", errorMsg);
        showNotification && showNotification(
          errorMsg || "Hubo un problema al eliminar.",
          "error"
        );
        return false;
      }

      setRecords(prev => prev.filter(r => r.id !== record.id));
      showNotification && showNotification("Registro eliminado correctamente.", "success");
      afterSuccess && afterSuccess();
      return true;
    } catch (error) {
      console.error("Error en handleDelete:", error);
      showNotification && showNotification("Error desconocido al eliminar.", "error");
      return false;
    }
  };
}
