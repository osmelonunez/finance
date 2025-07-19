export default function useHandleAdd({
  endpoint,
  field,
  isExpenses,
  token,
  newRecord,
  setNewRecord,
  setShowAddModal,
  setError,
  setRecords,
  showNotification,
  afterSuccess,
}) {
  return async function handleAdd(record) {
    const valueField = field || "cost";
    const value = record[valueField] !== undefined ? Number(record[valueField]) : undefined;
    const month_id = record.month_id !== undefined ? Number(record.month_id) : undefined;
    const year_id = record.year_id !== undefined ? Number(record.year_id) : undefined;
    const category_id = record.category_id !== undefined ? Number(record.category_id) : undefined;

    console.log("Checking new record in handleAdd:", record);

    if (!record.name) console.error("Missing field: name", record.name);
    if (!value) console.error(`Missing or invalid field: ${valueField}`, value);
    if (!month_id) console.error("Missing or invalid field: month_id", month_id);
    if (!year_id) console.error("Missing or invalid field: year_id", year_id);

    // Solo valida category_id si existe
    if ('category_id' in record && !category_id) {
      console.error("Missing or invalid field: category_id", category_id);
      showNotification && showNotification("All fields are required.", "error");
      return false;
    }

    if (
      !record.name ||
      !value ||
      !month_id ||
      !year_id ||
      (('category_id' in record) && !category_id)
    ) {
      showNotification && showNotification("All fields are required.", "error");
      return false;
    }

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          ...record,
          [valueField]: value,
          month_id,
          year_id,
          ...(category_id ? { category_id } : {})
        })
      });

      if (!response.ok) {
        const errorMsg = await response.text();
        setError && setError(errorMsg || "Error adding record.");
        showNotification && showNotification("Error adding record.", "error");
        return false;
      }

      const addedRecords = await response.json();
      setRecords && setRecords([...addedRecords]);
      setNewRecord && setNewRecord({});
      setShowAddModal && setShowAddModal(false);
      setError && setError("");
      showNotification && showNotification("Record added successfully.", "success");
      afterSuccess && afterSuccess();

      return true;
    } catch (error) {
      setError && setError(error.message || "Unknown error adding record.");
      showNotification && showNotification("Unknown error adding record.", "error");
      console.error(error);
      return false;
    }
  };
}
