// useHandleEdit.js
export default function useHandleEdit({
  endpoint,
  field,
  token,
  editingRecord,
  setEditingRecord,
  setShowEditModal,
  setError,
  setRecords,
  showNotification,
  afterSuccess
}) {
  // Puedes usar async o no, según cómo hagas la llamada
  return async function handleEdit(record) {
    // Validación fuerte: no debe ser null ni sin nombre
    if (!record || typeof record !== "object" || !record.name) {
      setError && setError("El registro a editar no es válido.");
      showNotification && showNotification("Error: El registro es inválido.", "error");
      console.warn("Intento de editar registro inválido:", record);
      return false;
    }

    try {
      // --- Tu lógica de actualización aquí ---
      // Ejemplo típico con fetch:
      const response = await fetch(`${endpoint}/${record.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(record)
      });

      if (!response.ok) {
        const errorMsg = await response.text();
        setError && setError(errorMsg || "Error al editar el registro.");
        showNotification && showNotification("Error al editar el registro.", "error");
        return false;
      }

      // Actualiza los datos locales si es necesario
      const updated = await response.json();
      setRecords && setRecords(prev =>
        prev.map(r => (r.id === updated.id ? updated : r))
      );

      // Opcional: limpia modal/errores
      setEditingRecord && setEditingRecord(null);
      setShowEditModal && setShowEditModal(false);
      setError && setError("");

      showNotification && showNotification("Registro actualizado correctamente.", "success");

      // Llama afterSuccess si quieres refrescar la lista
      afterSuccess && afterSuccess();

      return true;
    } catch (error) {
      setError && setError(error.message || "Error desconocido al editar.");
      showNotification && showNotification("Error desconocido al editar.", "error");
      console.error(error);
      return false;
    }
  };
}
