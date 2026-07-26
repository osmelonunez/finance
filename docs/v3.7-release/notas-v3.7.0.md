# Finance v3.7.0 - Presupuestos e Informes

Esta versión incorpora los espacios principales de **Presupuestos** e **Informes**, amplía el modelo de cuentas de ahorro y elimina el origen obsoleto de los movimientos.

## Presupuesto vigente

- Cada categoría puede tener un presupuesto mensual vigente.
- El presupuesto solo se edita desde el mes actual.
- El último presupuesto configurado continúa automáticamente en los meses siguientes.
- Modificar el presupuesto actual no cambia los importes aplicados en meses anteriores.
- Las categorías se siguen creando, editando y eliminando desde su módulo independiente.
- Las categorías nuevas aparecen automáticamente como `Sin presupuesto`.
- Una acción con confirmación permite quitar el presupuesto desde el mes actual sin modificar el histórico.
- Un presupuesto retirado puede volver a asignarse posteriormente.
- Los datos demo fuerzan un presupuesto inicial para todas las categorías, incluidas las que estuvieran explícitamente sin presupuesto.
- Al limpiar el demo se restaura el estado anterior de las categorías reactivadas y se eliminan los presupuestos creados exclusivamente por el demo.

## Seguimiento mensual

- Resumen de presupuesto total, gasto real, importe disponible y categorías en riesgo o excedidas.
- Barras de consumo por categoría.
- Alertas visuales al alcanzar el 80%, 90% y 100%.
- Filtros para mostrar todas las categorías, las que están en riesgo, las excedidas o las que no tienen presupuesto.
- Cálculo del gasto real a partir de todos los movimientos de tipo gasto, independientemente de la cuenta utilizada.
- Acceso directo desde Presupuestos a la gestión independiente de categorías para administradores y editores.

## Histórico

- Navegación por meses anteriores.
- Los meses históricos son de solo lectura.
- Cada mes muestra el último presupuesto que estaba vigente en ese momento.
- Se muestra la desviación entre presupuesto y gasto real, incluyendo cuánto se excedió una categoría.
- Los meses futuros no están disponibles.
- Acceso rápido para volver al mes actual.

## Dashboard

- Resumen del presupuesto correspondiente al mes seleccionado.
- Comparativa de gasto real frente a presupuesto total.
- Número de categorías que han superado su presupuesto.
- Enlace directo al detalle mensual de Presupuestos.

## Informes

- Nuevo acceso principal `Informes`.
- Diez estilos de correo, incorporando Recibo, Estado financiero, Magazine, Minimalista y Neón, seleccionables por separado para el informe mensual y anual.
- Branding compartido para emails con nombre, cabecera y pie centrado.
- Cabecera unificada con nombre de marca, título mensual o anual, texto descriptivo y periodo.
- Pie integrado y centrado, alineado con la identidad y versión del sitio.
- Enlace visible `Abrir Finance` en todas las plantillas, dirigido a la URL pública configurada sin mostrar la dirección en el contenido.
- Vista previa de cada plantilla con los datos reales y el periodo seleccionado, usando el mismo renderizador que el envío.
- Comparativas por mes, trimestre y año mediante dos desplegables generados desde la ventana de años configurada.
- Indicadores de ingresos, gastos, ahorro y balance con valores actual/anterior y variaciones absoluta y porcentual.
- Gráfico de evolución de ingresos, gastos, ahorro y balance para los últimos 6 o 12 meses y la ventana de años configurada.
- Controles para activar u ocultar cada serie sin recargar el informe.
- Selector único para las combinaciones válidas Libre, MoM y YoY, con selección automática de la referencia.
- Desglose por categoría, detección de categorías nuevas o sin gasto actual y rankings de los cinco mayores aumentos y reducciones.
- Filtros compartidos por categoría, banco, cuenta, tarjeta y préstamo en Resumen, Comparativas y Evolución.
- Exportación CSV contextual y vista específica para imprimir o guardar como PDF.
- Informes guardados por usuario para reutilizar secciones, periodos, modos y filtros.
- Consulta mensual y anual de ingresos, gastos, ahorro y balance.
- Desglose visual del gasto por categoría.
- Tabla de principales gastos del periodo.
- Configuración de reportes mensuales y anuales por correo.
- Historial de los últimos envíos y su estado.
- SMTP permanece como configuración técnica independiente dentro de Gestión.

## Cuentas de ahorro

- Clasificación de cuentas bancarias como corrientes o de ahorro.
- Saldo inicial y soporte para varias cuentas de ahorro.
- Cuenta de destino obligatoria al registrar una aportación de ahorro.
- Los gastos y tarjetas asociados a cuentas de ahorro descuentan de su saldo.
- Agregado `Savings Accounts` con desglose por cuenta en Dashboard e Informes.
- Todos los gastos consumen presupuesto independientemente de la cuenta utilizada.

## Datos y compatibilidad

- Nuevas migraciones `018_category_budgets.sql`, `019_budget_disabled_state.sql`, `020_saved_reports.sql`, `021_savings_accounts.sql`, `022_email_report_branding.sql` y `023_remove_record_source.sql`.
- Se elimina `records.source`: la cuenta o tarjeta asociada mediante `payment_method_id` determina el origen o destino financiero del movimiento.
- Los presupuestos mantienen categoría, mes de entrada en vigor, importe y campos de auditoría.
- El estado desactivado registra explícitamente que una categoría queda sin presupuesto, evitando heredar de nuevo un importe anterior.
- La combinación de categoría y mes es única.
- No se duplican importes de gasto: el gasto real se calcula desde `records`.
- No se pueden eliminar categorías con movimientos o histórico presupuestario.
- La versión visible en el pie de página pasa a `3.7.0`.

## Validación realizada

- Compilación completa del backend.
- Carga de las 31 plantillas Jinja.
- Inventario de 98 rutas y 104 combinaciones de ruta y método.
- Validación funcional sobre PostgreSQL aislado.
- Comprobación de edición en el mes actual, herencia del presupuesto, histórico de solo lectura y bloqueo de meses futuros.
- Comprobación del resumen de presupuesto en el dashboard.
- Arranque y health check del entorno local.
- Suite completa: 443 pruebas superadas y 76,02% de cobertura, con mínimo obligatorio del 65%.

## Artefactos previstos

- Imagen: `f1nanc3/finance:3.7.0`
- Imagen flotante: `f1nanc3/finance:latest`
- Tag Git previsto: `v3.7.0`
- Nombre previsto de la release: `Finance v3.7.0`

El tag, la release y la publicación de las imágenes todavía no se han creado.
