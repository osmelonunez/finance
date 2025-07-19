-- ELIMINAR DATOS DE PRUEBA (_devdata) ANTES DE CARGAR
DELETE FROM savings WHERE name LIKE '%_devdata';
DELETE FROM incomes WHERE name LIKE '%_devdata';
DELETE FROM expenses WHERE name LIKE '%_devdata';

-- ========== AHORROS ==========
INSERT INTO savings (name, amount, month_id, year_id, created_by_user_id, last_modified_by_user_id)
VALUES
('Vacaciones fija y alterna_devdata', 250.00, 1, 1, 1, 1),
('Coche_devdata', 300.00, 2, 1, 1, 1),
('Vacaciones fija y alterna_devdata', 250.00, 3, 1, 1, 1),
('Movil_devdata', 150.00, 4, 1, 1, 1),
('Vacaciones fija y alterna_devdata', 250.00, 5, 1, 1, 1),
('Coche_devdata', 300.00, 6, 1, 1, 1),
('Vacaciones fija y alterna_devdata', 250.00, 7, 1, 1, 1),
('Movil_devdata', 150.00, 8, 1, 1, 1),
('Vacaciones fija y alterna_devdata', 250.00, 9, 1, 1, 1),
('Coche_devdata', 300.00, 10, 1, 1, 1),
('Vacaciones fija y alterna_devdata', 250.00, 11, 1, 1, 1),
('Movil_devdata', 150.00, 12, 1, 1, 1),
('Vacaciones fija y alterna_devdata', 250.00, 1, 1, 1, 1),
('Coche_devdata', 300.00, 2, 1, 1, 1),
('Vacaciones fija y alterna_devdata', 250.00, 3, 1, 1, 1),
('Movil_devdata', 150.00, 4, 1, 1, 1),
('Vacaciones fija y alterna_devdata', 250.00, 5, 1, 1, 1),
('Coche_devdata', 300.00, 6, 1, 1, 1),
('Vacaciones fija y alterna_devdata', 250.00, 7, 1, 1, 1),
('Movil_devdata', 150.00, 8, 1, 1, 1),
('Vacaciones fija y alterna_devdata', 250.00, 9, 1, 1, 1),
('Coche_devdata', 300.00, 10, 1, 1, 1),
('Vacaciones fija y alterna_devdata', 250.00, 11, 1, 1, 1),
('Movil_devdata', 150.00, 12, 1, 1, 1);

-- ========== INGRESOS ==========
INSERT INTO incomes (name, amount, month_id, year_id, created_by_user_id, last_modified_by_user_id)
VALUES
('nomina 1_devdata', 1400.00, 1, 1, 1, 1),
('nomina 2_devdata', 1600.00, 1, 1, 1, 1),
('nomina 1_devdata', 1400.00, 2, 1, 1, 1),
('nomina 2_devdata', 1600.00, 2, 1, 1, 1),
('nomina 1_devdata', 1400.00, 3, 1, 1, 1),
('nomina 2_devdata', 1600.00, 3, 1, 1, 1),
('nomina 1_devdata', 1400.00, 4, 1, 1, 1),
('nomina 2_devdata', 1600.00, 4, 1, 1, 1),
('nomina 1_devdata', 1400.00, 5, 1, 1, 1),
('nomina 2_devdata', 1600.00, 5, 1, 1, 1),
('nomina 1_devdata', 1400.00, 6, 1, 1, 1),
('nomina 2_devdata', 1600.00, 6, 1, 1, 1),
('nomina 1_devdata', 1400.00, 7, 1, 1, 1),
('nomina 2_devdata', 1600.00, 7, 1, 1, 1),
('nomina 1_devdata', 1400.00, 8, 1, 1, 1),
('nomina 2_devdata', 1600.00, 8, 1, 1, 1),
('nomina 1_devdata', 1400.00, 9, 1, 1, 1),
('nomina 2_devdata', 1600.00, 9, 1, 1, 1),
('nomina 1_devdata', 1400.00, 10, 1, 1, 1),
('nomina 2_devdata', 1600.00, 10, 1, 1, 1),
('nomina 1_devdata', 1400.00, 11, 1, 1, 1),
('nomina 2_devdata', 1600.00, 11, 1, 1, 1),
('nomina 1_devdata', 1400.00, 12, 1, 1, 1),
('nomina 2_devdata', 1600.00, 12, 1, 1, 1);

-- ENERO
INSERT INTO expenses (name, cost, month_id, year_id, category_id, source, created_by_user_id, last_modified_by_user_id) VALUES
('Renta_devdata', 900.00, 1, 1, 1, 'current_month', 1, 1),
('Movi-Fibra_devdata', 50.00, 1, 1, 1, 'current_month', 1, 1),
('Agua_devdata', 25.00, 1, 1, 1, 'current_month', 1, 1),
('Gas_devdata', 30.00, 1, 1, 1, 'current_month', 1, 1),
('Comunidad_devdata', 40.00, 1, 1, 1, 'current_month', 1, 1),
('Gimnasio_devdata', 40.00, 1, 1, 7, 'current_month', 1, 1),
('Transporte público_devdata', 45.00, 1, 1, 5, 'current_month', 1, 1),
('Supermercado_devdata', 395.00, 1, 1, 3, 'current_month', 1, 1),
('Suscripciones_devdata', 30.00, 1, 1, 9, 'current_month', 1, 1),
('Farmacia_devdata', 10.00, 1, 1, 8, 'current_month', 1, 1),
('Ocio_devdata', 20.00, 1, 1, 4, 'current_month', 1, 1),
('Ropa_devdata', 60.00, 1, 1, 6, 'current_month', 1, 1);

-- FEBRERO
INSERT INTO expenses (name, cost, month_id, year_id, category_id, source, created_by_user_id, last_modified_by_user_id) VALUES
('Renta_devdata', 900.00, 2, 1, 1, 'current_month', 1, 1),
('Movi-Fibra_devdata', 50.00, 2, 1, 1, 'current_month', 1, 1),
('Agua_devdata', 25.00, 2, 1, 1, 'current_month', 1, 1),
('Gas_devdata', 30.00, 2, 1, 1, 'current_month', 1, 1),
('Comunidad_devdata', 40.00, 2, 1, 1, 'current_month', 1, 1),
('Gimnasio_devdata', 40.00, 2, 1, 7, 'current_month', 1, 1),
('Transporte público_devdata', 45.00, 2, 1, 5, 'current_month', 1, 1),
('Supermercado_devdata', 388.00, 2, 1, 3, 'current_month', 1, 1),
('Suscripciones_devdata', 30.00, 2, 1, 9, 'current_month', 1, 1),
('Ocio_devdata', 35.00, 2, 1, 4, 'current_month', 1, 1);

-- MARZO
INSERT INTO expenses (name, cost, month_id, year_id, category_id, source, created_by_user_id, last_modified_by_user_id) VALUES
('Renta_devdata', 900.00, 3, 1, 1, 'current_month', 1, 1),
('Movi-Fibra_devdata', 50.00, 3, 1, 1, 'current_month', 1, 1),
('Agua_devdata', 25.00, 3, 1, 1, 'current_month', 1, 1),
('Gas_devdata', 30.00, 3, 1, 1, 'current_month', 1, 1),
('Comunidad_devdata', 40.00, 3, 1, 1, 'current_month', 1, 1),
('Gimnasio_devdata', 40.00, 3, 1, 7, 'current_month', 1, 1),
('Transporte público_devdata', 45.00, 3, 1, 5, 'current_month', 1, 1),
('Supermercado_devdata', 405.00, 3, 1, 3, 'current_month', 1, 1),
('Suscripciones_devdata', 30.00, 3, 1, 9, 'current_month', 1, 1),
('Ocio_devdata', 80.00, 3, 1, 4, 'current_month', 1, 1),
('Farmacia_devdata', 25.00, 3, 1, 8, 'current_month', 1, 1);

-- ABRIL
INSERT INTO expenses (name, cost, month_id, year_id, category_id, source, created_by_user_id, last_modified_by_user_id) VALUES
('Renta_devdata', 900.00, 4, 1, 1, 'current_month', 1, 1),
('Movi-Fibra_devdata', 50.00, 4, 1, 1, 'current_month', 1, 1),
('Agua_devdata', 25.00, 4, 1, 1, 'current_month', 1, 1),
('Gas_devdata', 30.00, 4, 1, 1, 'current_month', 1, 1),
('Comunidad_devdata', 40.00, 4, 1, 1, 'current_month', 1, 1),
('Gimnasio_devdata', 40.00, 4, 1, 7, 'current_month', 1, 1),
('Transporte público_devdata', 45.00, 4, 1, 5, 'current_month', 1, 1),
('Supermercado_devdata', 412.00, 4, 1, 3, 'current_month', 1, 1),
('Suscripciones_devdata', 30.00, 4, 1, 9, 'current_month', 1, 1),
('Ocio_devdata', 75.00, 4, 1, 4, 'current_month', 1, 1),
('Farmacia_devdata', 13.00, 4, 1, 8, 'current_month', 1, 1),
('Reparación hogar_devdata', 130.00, 4, 1, 2, 'current_month', 1, 1);

-- MAYO
INSERT INTO expenses (name, cost, month_id, year_id, category_id, source, created_by_user_id, last_modified_by_user_id) VALUES
('Renta_devdata', 900.00, 5, 1, 1, 'current_month', 1, 1),
('Movi-Fibra_devdata', 50.00, 5, 1, 1, 'current_month', 1, 1),
('Agua_devdata', 25.00, 5, 1, 1, 'current_month', 1, 1),
('Gas_devdata', 30.00, 5, 1, 1, 'current_month', 1, 1),
('Comunidad_devdata', 40.00, 5, 1, 1, 'current_month', 1, 1),
('Gimnasio_devdata', 40.00, 5, 1, 7, 'current_month', 1, 1),
('Transporte público_devdata', 45.00, 5, 1, 5, 'current_month', 1, 1),
('Supermercado_devdata', 410.00, 5, 1, 3, 'current_month', 1, 1),
('Suscripciones_devdata', 30.00, 5, 1, 9, 'current_month', 1, 1),
('Ocio_devdata', 25.00, 5, 1, 4, 'current_month', 1, 1);

-- JUNIO
INSERT INTO expenses (name, cost, month_id, year_id, category_id, source, created_by_user_id, last_modified_by_user_id) VALUES
('Renta_devdata', 900.00, 6, 1, 1, 'current_month', 1, 1),
('Movi-Fibra_devdata', 50.00, 6, 1, 1, 'current_month', 1, 1),
('Agua_devdata', 25.00, 6, 1, 1, 'current_month', 1, 1),
('Gas_devdata', 30.00, 6, 1, 1, 'current_month', 1, 1),
('Comunidad_devdata', 40.00, 6, 1, 1, 'current_month', 1, 1),
('Gimnasio_devdata', 40.00, 6, 1, 7, 'current_month', 1, 1),
('Transporte público_devdata', 45.00, 6, 1, 5, 'current_month', 1, 1),
('Supermercado_devdata', 405.00, 6, 1, 3, 'current_month', 1, 1),
('Suscripciones_devdata', 30.00, 6, 1, 9, 'current_month', 1, 1),
('Farmacia_devdata', 18.00, 6, 1, 8, 'current_month', 1, 1),
('Ocio_devdata', 65.00, 6, 1, 4, 'current_month', 1, 1),
('Vacaciones verano_devdata', 1000.00, 6, 1, 4, 'general_savings', 1, 1);

-- JULIO
INSERT INTO expenses (name, cost, month_id, year_id, category_id, source, created_by_user_id, last_modified_by_user_id) VALUES
('Renta_devdata', 900.00, 7, 1, 1, 'current_month', 1, 1),
('Movi-Fibra_devdata', 50.00, 7, 1, 1, 'current_month', 1, 1),
('Agua_devdata', 25.00, 7, 1, 1, 'current_month', 1, 1),
('Gas_devdata', 30.00, 7, 1, 1, 'current_month', 1, 1),
('Comunidad_devdata', 40.00, 7, 1, 1, 'current_month', 1, 1),
('Gimnasio_devdata', 40.00, 7, 1, 7, 'current_month', 1, 1),
('Transporte público_devdata', 45.00, 7, 1, 5, 'current_month', 1, 1),
('Supermercado_devdata', 420.00, 7, 1, 3, 'current_month', 1, 1),
('Suscripciones_devdata', 30.00, 7, 1, 9, 'current_month', 1, 1),
('Ocio_devdata', 80.00, 7, 1, 4, 'current_month', 1, 1),
('Vacaciones verano_devdata', 1000.00, 7, 1, 4, 'general_savings', 1, 1),
('Ropa_devdata', 100.00, 7, 1, 6, 'current_month', 1, 1);

-- AGOSTO
INSERT INTO expenses (name, cost, month_id, year_id, category_id, source, created_by_user_id, last_modified_by_user_id) VALUES
('Renta_devdata', 900.00, 8, 1, 1, 'current_month', 1, 1),
('Movi-Fibra_devdata', 50.00, 8, 1, 1, 'current_month', 1, 1),
('Agua_devdata', 25.00, 8, 1, 1, 'current_month', 1, 1),
('Gas_devdata', 30.00, 8, 1, 1, 'current_month', 1, 1),
('Comunidad_devdata', 40.00, 8, 1, 1, 'current_month', 1, 1),
('Gimnasio_devdata', 40.00, 8, 1, 7, 'current_month', 1, 1),
('Transporte público_devdata', 45.00, 8, 1, 5, 'current_month', 1, 1),
('Supermercado_devdata', 410.00, 8, 1, 3, 'current_month', 1, 1),
('Suscripciones_devdata', 30.00, 8, 1, 9, 'current_month', 1, 1),
('Ocio_devdata', 90.00, 8, 1, 4, 'current_month', 1, 1);

-- SEPTIEMBRE
INSERT INTO expenses (name, cost, month_id, year_id, category_id, source, created_by_user_id, last_modified_by_user_id) VALUES
('Renta_devdata', 900.00, 9, 1, 1, 'current_month', 1, 1),
('Movi-Fibra_devdata', 50.00, 9, 1, 1, 'current_month', 1, 1),
('Agua_devdata', 25.00, 9, 1, 1, 'current_month', 1, 1),
('Gas_devdata', 30.00, 9, 1, 1, 'current_month', 1, 1),
('Comunidad_devdata', 40.00, 9, 1, 1, 'current_month', 1, 1),
('Gimnasio_devdata', 40.00, 9, 1, 7, 'current_month', 1, 1),
('Transporte público_devdata', 45.00, 9, 1, 5, 'current_month', 1, 1),
('Supermercado_devdata', 400.00, 9, 1, 3, 'current_month', 1, 1),
('Suscripciones_devdata', 30.00, 9, 1, 9, 'current_month', 1, 1),
('Farmacia_devdata', 13.00, 9, 1, 8, 'current_month', 1, 1),
('Ropa_devdata', 45.00, 9, 1, 6, 'current_month', 1, 1);

-- OCTUBRE
INSERT INTO expenses (name, cost, month_id, year_id, category_id, source, created_by_user_id, last_modified_by_user_id) VALUES
('Renta_devdata', 900.00, 10, 1, 1, 'current_month', 1, 1),
('Movi-Fibra_devdata', 50.00, 10, 1, 1, 'current_month', 1, 1),
('Agua_devdata', 25.00, 10, 1, 1, 'current_month', 1, 1),
('Gas_devdata', 30.00, 10, 1, 1, 'current_month', 1, 1),
('Comunidad_devdata', 40.00, 10, 1, 1, 'current_month', 1, 1),
('Gimnasio_devdata', 40.00, 10, 1, 7, 'current_month', 1, 1),
('Transporte público_devdata', 45.00, 10, 1, 5, 'current_month', 1, 1),
('Supermercado_devdata', 405.00, 10, 1, 3, 'current_month', 1, 1),
('Suscripciones_devdata', 30.00, 10, 1, 9, 'current_month', 1, 1),
('Ocio_devdata', 50.00, 10, 1, 4, 'current_month', 1, 1);

-- NOVIEMBRE
INSERT INTO expenses (name, cost, month_id, year_id, category_id, source, created_by_user_id, last_modified_by_user_id) VALUES
('Renta_devdata', 900.00, 11, 1, 1, 'current_month', 1, 1),
('Movi-Fibra_devdata', 50.00, 11, 1, 1, 'current_month', 1, 1),
('Agua_devdata', 25.00, 11, 1, 1, 'current_month', 1, 1),
('Gas_devdata', 30.00, 11, 1, 1, 'current_month', 1, 1),
('Comunidad_devdata', 40.00, 11, 1, 1, 'current_month', 1, 1),
('Gimnasio_devdata', 40.00, 11, 1, 7, 'current_month', 1, 1),
('Transporte público_devdata', 45.00, 11, 1, 5, 'current_month', 1, 1),
('Supermercado_devdata', 395.00, 11, 1, 3, 'current_month', 1, 1),
('Suscripciones_devdata', 30.00, 11, 1, 9, 'current_month', 1, 1),
('Ocio_devdata', 40.00, 11, 1, 4, 'current_month', 1, 1),
('Farmacia_devdata', 28.00, 11, 1, 8, 'current_month', 1, 1);

-- DICIEMBRE
INSERT INTO expenses (name, cost, month_id, year_id, category_id, source, created_by_user_id, last_modified_by_user_id) VALUES
('Renta_devdata', 900.00, 12, 1, 1, 'current_month', 1, 1),
('Movi-Fibra_devdata', 50.00, 12, 1, 1, 'current_month', 1, 1),
('Agua_devdata', 25.00, 12, 1, 1, 'current_month', 1, 1),
('Gas_devdata', 30.00, 12, 1, 1, 'current_month', 1, 1),
('Comunidad_devdata', 40.00, 12, 1, 1, 'current_month', 1, 1),
('Gimnasio_devdata', 40.00, 12, 1, 7, 'current_month', 1, 1),
('Transporte público_devdata', 45.00, 12, 1, 5, 'current_month', 1, 1),
('Supermercado_devdata', 405.00, 12, 1, 3, 'current_month', 1, 1),
('Suscripciones_devdata', 30.00, 12, 1, 9, 'current_month', 1, 1),
('Ocio_devdata', 90.00, 12, 1, 4, 'current_month', 1, 1),
('Ropa_devdata', 80.00, 12, 1, 6, 'current_month', 1, 1);
