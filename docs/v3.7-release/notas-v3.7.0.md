# Finance v3.7.0 - Presupuestos por categoría

Esta versión incorpora un espacio principal de **Presupuestos** para comparar el gasto mensual esperado con el gasto real de cada categoría.

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
- Cálculo del gasto real a partir de los movimientos de tipo gasto y origen mensual.
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
- Ocho estilos de correo, incorporando Recibo, Estado financiero y Magazine, seleccionables por separado para el informe mensual y anual.
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

## Datos y compatibilidad

- Nuevas migraciones `018_category_budgets.sql`, `019_budget_disabled_state.sql` y `020_saved_reports.sql`.
- Los presupuestos mantienen categoría, mes de entrada en vigor, importe y campos de auditoría.
- El estado desactivado registra explícitamente que una categoría queda sin presupuesto, evitando heredar de nuevo un importe anterior.
- La combinación de categoría y mes es única.
- No se duplican importes de gasto: el gasto real se calcula desde `records`.
- No se pueden eliminar categorías con movimientos o histórico presupuestario.
- La versión visible en el pie de página pasa a `3.7.0`.

## Validación realizada

- Compilación completa del backend.
- Carga de las 30 plantillas Jinja.
- Inventario de 88 rutas y 94 combinaciones de ruta y método.
- Validación funcional sobre PostgreSQL aislado.
- Comprobación de edición en el mes actual, herencia del presupuesto, histórico de solo lectura y bloqueo de meses futuros.
- Comprobación del resumen de presupuesto en el dashboard.
- Arranque y health check del entorno local.
- Suite completa: 349 pruebas superadas y 70,59% de cobertura, con mínimo obligatorio del 65%.

## Artefactos previstos

- Imagen: `f1nanc3/finance:3.7.0`
- Imagen flotante: `f1nanc3/finance:latest`
- Tag Git previsto: `v3.7.0`
- Nombre previsto de la release: `Finance v3.7.0`

El tag, la release y la publicación de las imágenes todavía no se han creado.
