export default function useHandleEdit({
  endpoint,
  field,
  token,
  setError,
  setRecords,
  showNotification,
  afterSuccess,
}) {
  return async function handleEdit(updatedRecord) {
    try {
      // Construye el body dinámicamente según el campo principal
      const valueField = field || "cost";
      const value = updatedRecord[valueField] !== undefined
        ? Number(updatedRecord[valueField])
        : undefined;

      const response = await fetch(`${endpoint}/${updatedRecord.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          ...updatedRecord,
          [valueField]: value,
        })
      });

      if (!response.ok) {
        const errorMsg = await response.text();
        setError && setError(errorMsg || "Error updating record.");
        showNotification && showNotification("Error updating record.", "error");
        return false;
      }

      // Si tu backend devuelve el array actualizado de registros, úsalo:
      const updatedRecords = await response.json();
      if (Array.isArray(updatedRecords) && setRecords) {
        setRecords([...updatedRecords]);
      }

      setError && setError("");
      showNotification && showNotification("Record updated successfully.", "success");

      // Refresca los datos desde el backend
      afterSuccess && afterSuccess();

      return true;
    } catch (error) {
      setError && setError(error.message || "Unknown error updating record.");
      showNotification && showNotification("Unknown error updating record.", "error");
      console.error(error);
      return false;
    }
  };
}
