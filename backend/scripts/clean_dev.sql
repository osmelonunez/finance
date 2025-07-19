-- ELIMINAR DATOS DE PRUEBA (_devdata) ANTES DE CARGAR
DELETE FROM savings WHERE name LIKE '%_devdata';
DELETE FROM incomes WHERE name LIKE '%_devdata';
DELETE FROM expenses WHERE name LIKE '%_devdata';
