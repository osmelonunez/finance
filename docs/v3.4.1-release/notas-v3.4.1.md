# v3.4.1 - Edición de usos de préstamo

## Resumen

Esta versión patch completa la gestión de los usos registrados dentro de un préstamo. Los usos ahora se pueden editar directamente desde el historial con el mismo patrón de acciones utilizado en cuentas y tarjetas.

## Cambios

- Botón **Editar** para cada uso de préstamo.
- Edición de concepto, categoría, fecha, importe y comentario.
- Acciones **Cancelar**, **Guardar** y **Eliminar** visibles durante la edición.
- Conservación de la página activa después de guardar o eliminar.
- Validaciones de concepto, importe, fecha y comentario en backend.
- Actualización de `updated_at` y `updated_by` al guardar.
- Registro estructurado del evento `loan_usage_update`.
- Columnas reorganizadas como Concepto, Categoría, Fecha, Importe y Comentario.
- Fondo blanco para los registros y ancho reservado para las acciones.

## Compatibilidad

- No requiere una migración de base de datos.
- No modifica los datos existentes.
- Mantiene las rutas y el comportamiento previo de creación y eliminación.

## Despliegue

- Imagen: `f1nanc3/finance:3.4.1`
- Tag Git previsto: `v3.4.1`

## Validación

- Compilación de Python y plantilla Jinja.
- `git diff --check`.
- Construcción y arranque del entorno Docker de desarrollo.
- Comprobación de conexión a la base de datos y arranque de Gunicorn.
