# v3.9.0 - Bank record imports / Importacion de registros bancarios

## English

- Add integrated ING statement imports to Expenses and Incomes.
- Support legacy `.xls` and modern `.xlsx` files with validation and preview before saving.
- Map ING value date, category, description and amount to Finance records.
- Require one existing active card for all imported expenses.
- Match ING categories to Finance categories and highlight rows that need manual mapping.
- Allow editing concepts and descriptions, removing rows, and confirming imports atomically.
- Normalize common merchants and apply category rules for Amazon, AHORRAMAS, Uber, transport, pharmacies, leisure, iCloud and PayPal.
- Group monthly Amazon purchases while preserving an expandable breakdown of the original movements.
- Subtract Amazon card refunds from the corresponding monthly Amazon expense group and exclude them from income imports.
- Import positive movements separately from Incomes, classifying incomes, refunds and transfers; transfers are unselected by default.
- Expand automated coverage and update the endpoint catalog to 99 routes and 107 endpoint-method combinations.

## Espanol

- Se incorpora la importacion integrada de extractos ING en Gastos e Ingresos.
- Se admiten ficheros `.xls` antiguos y `.xlsx` modernos, con validacion y previsualizacion antes de guardar.
- Se utilizan la fecha valor, categoria, descripcion e importe de ING para crear los registros de Finance.
- Todos los gastos de una importacion requieren una tarjeta activa ya existente.
- Las categorias de ING se relacionan con las categorias de Finance y se resaltan las filas que necesitan asignacion manual.
- Se pueden editar concepto y descripcion, eliminar filas y confirmar la importacion de forma atomica.
- Se normalizan comercios habituales y se aplican reglas de categoria para Amazon, AHORRAMAS, Uber, transporte, farmacias, ocio, iCloud y PayPal.
- Las compras de Amazon se agrupan mensualmente y mantienen un desglose desplegable de los movimientos originales.
- Las devoluciones de tarjeta de Amazon se descuentan del grupo mensual correspondiente y se excluyen de la importacion de ingresos.
- Los movimientos positivos se importan por separado desde Ingresos y se clasifican como ingresos, devoluciones o transferencias; las transferencias quedan desmarcadas por defecto.
- Se amplia la cobertura automatizada y se actualiza el catalogo a 99 rutas y 107 combinaciones endpoint-metodo.
