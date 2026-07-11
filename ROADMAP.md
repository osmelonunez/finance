# Roadmap

Este roadmap separa lo ya completado y las ideas futuras a valorar. Las ideas no estan comprometidas con una version concreta y pueden reordenarse segun prioridad.

## Versiones completadas

### v3.1.0 - Hardening, operacion y rendimiento

Estado: completado.

Incluye:
- Hardening operativo de la aplicacion.
- Mejoras de rendimiento y mantenibilidad.
- Capa versionada de plantillas de reportes `v1`.
- Modulo comun de validaciones.
- Mejoras base para despliegue, logs y operacion.

### v3.2.0 - Loans and Banks

Estado: completado.

Incluye:
- Gestion de prestamos solicitados.
- Bancos gestionados desde el modulo de gestion.
- Vinculacion de cuentas/tarjetas a bancos.
- Pagos mensuales de prestamos registrados como gastos.
- Reduccion automatica de deuda al pagar prestamos.
- Datos demo con prestamos, bancos y pagos.
- Tarjetas de resumen de prestamos en dashboard y pagina de prestamos.

### v3.3.0 - Mortgage and Interest Loan Improvements

Estado: completado.

Incluye:
- Tipos de prestamo: sin intereses, con intereses e hipoteca.
- Campo `Total a devolver`.
- Pendiente calculado como `total a devolver - pagado`.
- Desglose de pagos hipotecarios entre amortizacion e intereses.
- Interes textual para hipotecas, por ejemplo `2,10 (EURIB+0.59)`.
- Edicion completa de prestamos desde el detalle.
- Recalculo de plazos al cambiar fecha de inicio.
- Recalculo de cuotas pagadas segun fecha de inicio.
- Usos de prestamo con historial y confirmacion de eliminacion.
- Mejoras en dashboard y resumen de prestamos.
- Migraciones `011`, `012` y `013`.

### v3.4.0 - Robustez de datos y seguridad de UX

Estado: completado.

Objetivo: estabilizar la aplicacion despues de los cambios grandes en prestamos, hipotecas e intereses.

Mas detalles:
- [Detalle de v3.4 en espanol](docs/v3.4-planning/detalles-v3.4.md)
- [v3.4 details in English](docs/v3.4-planning/v3.4-details.md)

Bloques implementados:

#### Limites de longitud
- Concepto de registro: 40 caracteres.
- Comentario de registro: 500 caracteres.
- Nombre de categoria: 40 caracteres.
- Descripcion de categoria: 500 caracteres.
- Nombre de cuenta/tarjeta: 40 caracteres.
- Nombre de banco: 40 caracteres.
- Nombre de prestamo: 40 caracteres.
- Descripcion de prestamo: 500 caracteres.
- Concepto de uso de prestamo: 40 caracteres.
- Comentario de uso de prestamo: 500 caracteres.
- Validaciones en backend, UI y constraints en base de datos.

#### Proteccion anti doble envio
- Deshabilitar botones al enviar formularios criticos.
- Mostrar estados como `Guardando`, `Creando`, `Eliminando` o `Procesando`.
- Proteger altas, ediciones, duplicados, eliminaciones, reset, demo data y botones asociados por `form`.
- Evitar registros duplicados por doble click.

#### Confirmaciones destructivas consistentes
- Unificar modales para eliminar registros, prestamos, usos de prestamo, categorias, bancos, cuentas/tarjetas y demo data.
- Mostrar claramente el objeto afectado.
- Mantener boton destructivo con estilo danger y boton cancelar visible.
- Mantener doble confirmacion para reset de base de datos.

#### Auditoria visual minima
- Mostrar Creado y Ultima edicion en detalle de registros y detalle de prestamos.
- Mantenerlo discreto para no competir con los datos financieros.

#### Logs de eventos de negocio
- Estandarizar logs para registros, prestamos, usos de prestamo, categorias, bancos, metodos de pago y datos demo.
- Agregar prefijo `[DEMO DATA]` y conteos por entidad al seed/clear de datos demo.

#### Gestion y prestamos
- Separar Gestion en Bancos, Cuentas y Tarjetas.
- Igualar acciones de bancos con cuentas/tarjetas: Editar, Cancelar, Guardar y Eliminar.
- Bloquear eliminacion de bancos usados por cuentas/tarjetas o prestamos.
- Autoexcluir de analiticas los prestamos Pagado o Cancelado.
- Mejorar validacion visual de uso de prestamo.
- Usar selector mensual al editar fecha de inicio de prestamo.

Migracion:
- `014_data_robustness_constraints.sql`

Validacion:
- `python3 -m compileall backend`
- `git diff --check`
- `make up`
- Pruebas manuales de validacion, formularios, modales, gestion, datos demo y prestamos.

## Ideas futuras

Estas ideas no estan comprometidas todavia y pueden moverse segun prioridad.

### Cuentas y tarjetas 2.0

Objetivo: mejorar el modelo funcional de cuentas/tarjetas y su relacion con bancos y gastos.

Ideas:
- Estado activo/inactivo para cuentas y tarjetas.
- Evitar eliminacion si existen registros asociados.
- Vista de detalle de cuenta/tarjeta.
- Resumen de gasto por cuenta/tarjeta.
- Resumen por banco con cuentas y tarjetas vinculadas.
- Mejoras en filtros por banco, cuenta y tarjeta.

### Presupuestos por categoria

Objetivo: controlar gasto mensual esperado frente a gasto real.

Ideas:
- Presupuesto mensual por categoria.
- Barras de consumo por categoria.
- Alertas visuales al 80%, 90% y 100%.
- Dashboard con categorias fuera de presupuesto.
- Comparativa presupuesto vs gasto real.

### Importador bancario CSV

Objetivo: acelerar el registro de movimientos desde extractos bancarios.

Ideas:
- Importar ficheros CSV.
- Mapeo manual de columnas.
- Previsualizacion antes de insertar.
- Deteccion de posibles duplicados.
- Plantillas de mapeo por banco.
- Reglas basicas por concepto/categoria.

### Cierre mensual

Objetivo: crear un flujo guiado para revisar y cerrar cada mes.

Ideas:
- Checklist de cierre mensual.
- Snapshot mensual de ingresos, gastos, ahorros, prestamos y balance.
- Estado opcional de mes cerrado.
- Comparativa con el mes anterior.
- Notas/resumen del mes.

### Prestamos como modulo opcional

Objetivo: permitir activar o desactivar toda la funcionalidad de prestamos desde administracion.

Ideas:
- Opcion global en Gestion o Sistema para activar/desactivar el modulo de prestamos.
- Ocultar la navegacion de Prestamos cuando el modulo este desactivado.
- Ocultar tarjetas, graficas y totales relacionados con prestamos en el dashboard.
- Ocultar campos de pago de prestamo en gastos si el modulo esta desactivado.
- Mantener los datos existentes sin borrarlos al desactivar el modulo.
- Bloquear rutas de prestamos o redirigir con un mensaje claro cuando el modulo este desactivado.
- Reflejar el estado del modulo en configuracion y documentacion operativa.

### Actualizacion de permisos por roles

Objetivo: hacer mas flexible el control de acceso segun rol y accion dentro de la aplicacion.

Ideas:
- Revisar permisos actuales de `admin`, `editor` y `user`.
- Definir matriz de permisos por modulo: registros, prestamos, gestion, reportes, backups y sistema.
- Permitir permisos mas granulares para crear, editar, eliminar y solo consultar.
- Evaluar si conviene permitir roles personalizados desde administracion.
- Mostrar/ocultar acciones de la UI segun permisos reales del usuario.
- Bloquear rutas backend aunque una accion no sea visible en la interfaz.
- Documentar claramente que puede hacer cada rol.

### Otras ideas a valorar

- Adjuntar facturas/recibos a gastos.
- Exportacion de reportes a PDF.
- Plantillas de reportes `v2` y opciones de branding.
- Evolucion de i18n hacia estructura modular.
- Notificaciones internas y recordatorios.
- Reglas automaticas por categoria/origen/cuenta.
- Comparativas avanzadas por periodos (MoM/YoY).
- Soporte multi-moneda.
- API tokens para integraciones externas.
- Metricas operativas basicas: latencias por ruta y tasa de errores.
- Retencion configurable de logs de negocio en base de datos.
- Mejora de rendimiento en listados masivos/exportaciones.
- Scripts y documentacion operativa de mantenimiento.
