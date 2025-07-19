import ModalOverlay from "./ModalOverlay";
import AddRecordForm from "./AddRecordForm";
import { useEffect } from "react";

export default function AddRecordModal(props) {
  useEffect(() => {
    if (!props.newRecord.source) {
      props.setNewRecord((prev) => ({
        ...prev,
        source: "current_month"
      }));
    }
  }, [props.newRecord.source, props.setNewRecord]);

  const handleConfirm = (data) => {
    if (data && data.multiAdd) {
      const { selectedYears, selectedMonths } = data;
      const recordsToAdd = [];

      selectedYears.forEach(yearId => {
        selectedMonths.forEach(monthId => {
          // Forzar find usando number, y tomar el id exacto del objeto
          const yearObj = props.years.find(y => Number(y.id) === Number(yearId));
          const monthObj = props.months.find(m => Number(m.id) === Number(monthId));
          if (yearObj && monthObj) {
            recordsToAdd.push({
              ...props.newRecord,
              year_id: yearObj.id,
              month_id: monthObj.id
            });
          } else {
            // Debug si algo sale mal
            console.log('NO FOUND:', { yearId, monthId, yearObj, monthObj, years: props.years, months: props.months });
          }
        });
      });

      if (!recordsToAdd.length) return; // Previene enviar vacíos

      recordsToAdd.forEach(r => props.onConfirm(r));
      props.onClose();
    } else {
      props.onConfirm(props.newRecord);
      props.onClose();
    }
  };

  return (
    <ModalOverlay isOpen={props.isOpen} onClose={props.onClose}>
      <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl p-6 space-y-6 relative">
        <AddRecordForm
          {...props}
          onCancel={props.onClose}
          onSubmit={handleConfirm}
        />
      </div>
    </ModalOverlay>
  );
}
