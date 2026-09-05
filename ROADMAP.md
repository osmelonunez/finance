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

### v3.4.1 - Edicion de usos de prestamo

Estado: completado.

Objetivo: completar la gestion de los usos de prestamo sin introducir cambios de esquema.

Incluye:
- Edicion en linea de concepto, categoria, fecha, importe y comentario.
- Acciones consistentes de Editar, Cancelar, Guardar y Eliminar.
- Validacion backend y actualizacion de los campos de auditoria.
- Tabla reorganizada con fondo blanco y espacio estable para las acciones.
- [Notas de release en espanol](docs/v3.4.1-release/notas-v3.4.1.md)
- [Release notes in English](docs/v3.4.1-release/v3.4.1-release-notes.md)

### v3.5.0 - Cuentas y tarjetas 2.0

Estado: completado.

Objetivo: convertir bancos, cuentas y tarjetas en un espacio funcional independiente, conectado con movimientos y protegido por reglas de integridad.

Incluye:
- Espacio principal `Cuentas y tarjetas` en `/payment-methods`, separado de Gestion.
- Navegacion interna mediante KPI, Relaciones, Bancos, Cuentas y Tarjetas.
- Formulario unico y contextual para crear bancos, cuentas o tarjetas.
- Banco activo obligatorio al crear o editar una cuenta o tarjeta.
- Desactivacion automatica de cuentas y tarjetas al desactivar su banco.
- Bloqueo de eliminacion de cuentas o tarjetas con movimientos asociados.
- Altas y duplicados de movimientos limitados a cuentas y tarjetas activas.
- Vistas de detalle de bancos, cuentas y tarjetas con estado, referencia, gasto y numero de movimientos.
- Historial de movimientos paginado en bloques de diez y cargado desde el servidor.
- Filtros de gastos independientes por banco, cuenta y tarjeta, incluyendo entidades inactivas para consultar el historico.
- KPI de entidades activas y gasto mensual.
- Selector de año y graficas de gasto mensual, anual, total y comparativa.
- Estados vacios para ambitos sin gasto.
- Vista Relaciones agrupada por banco y ordenada por numero de elementos vinculados.
- Formato monetario y numerico localizado en tablas, indicadores y graficas.
- Redirecciones compatibles desde las antiguas rutas de Gestion.
- Suite automatica de regresion con PostgreSQL aislado, inventario de rutas, permisos, CSRF y flujos CRUD.
- Catalogo versionado de endpoints e informes historicos de pruebas.
- Sin cambios de esquema ni modificacion de datos existentes.
- [Detalle de v3.5 en espanol](docs/v3.5-planning/detalles-v3.5.md)
- [v3.5 details in English](docs/v3.5-planning/v3.5-details.md)
- [Notas de release en espanol](docs/v3.5-release/notas-v3.5.0.md)
- [Release notes in English](docs/v3.5-release/v3.5.0-release-notes.md)

### v3.6.0 - Banca e integracion de prestamos

Estado: completado.

Objetivo: consolidar bancos, cuentas y tarjetas como un espacio bancario coherente e integrar la informacion financiera de los prestamos sin confundir deuda, capital utilizado y saldo disponible.

Incluye:
- Bloqueo explicito de eliminacion cuando existen movimientos asociados.
- Estado activo/inactivo aplicado en altas, ediciones y duplicados de movimientos.
- Desactivacion automatica de cuentas y tarjetas al desactivar su banco.
- Banco obligatorio para crear o editar cuentas; cuenta activa obligatoria para crear o editar tarjetas, validado en UI y backend.
- Espacio independiente `Banca` en `/payment-methods`, fuera de Gestion, con navegacion KPI, Relaciones, Bancos, Cuentas y Tarjetas.
- Formulario unico y contextual para crear bancos, cuentas o tarjetas.
- Vistas de detalle para bancos, cuentas y tarjetas con estado, referencia, metricas de gasto y numero de movimientos.
- Historial paginado de movimientos, cargado en bloques de diez desde el servidor.
- Filtros de gastos independientes por banco, cuenta y tarjeta.
- KPI con conteos de entidades activas, gasto mensual y graficas por banco, cuenta o tarjeta.
- Selector de año, estados vacios y graficas de gasto mensual, anual, total y comparativa.
- Vista Relaciones ordenada por bancos con mayor numero de cuentas y tarjetas vinculadas y jerarquia visual Banco → Cuenta → Tarjeta.
- Tarjetas vinculadas a cuentas mediante conexiones directas, con compatibilidad para datos existentes todavía sin asignar.
- Prestamos asociados visibles en el detalle del banco, incluso cuando el banco no tiene cuentas.
- KPI bancarios de capital prestado, deuda pendiente, importe amortizado y cuota mensual.
- Mensaje especifico para bancos sin saldo que solo tienen prestamos, sin crear cuentas ficticias ni inferir saldo disponible.
- Los pagos de prestamos, incluidos capital e intereses, forman parte del gasto del banco; los usos del capital prestado no se contabilizan como gasto propio.
- Formato monetario y numerico localizado en toda la aplicacion.
- Redirecciones compatibles desde las antiguas rutas de Gestion y rutas renombradas.
- Suite automatica de regresion de release con PostgreSQL aislado, inventario de rutas, permisos, CSRF y flujos CRUD.
- Catalogo versionado de endpoints e informes Markdown por cada ejecucion de pruebas.
- Migracion `015_cards_linked_to_accounts.sql` para la relacion tarjeta-cuenta.
- [Notas de release en espanol](docs/v3.6-release/notas-v3.6.0.md)
- [Release notes in English](docs/v3.6-release/v3.6.0-release-notes.md)

### v3.6.1 - Nombres de cuentas y tarjetas por contexto

Estado: preparado.

Objetivo: corregir la unicidad global heredada de los metodos de pago para permitir nombres naturales repetidos cuando pertenecen a entidades padre diferentes.

Incluye:
- Nombres de cuenta unicos dentro de cada banco, pero reutilizables entre bancos distintos.
- Nombres de tarjeta sin restriccion de unicidad; la identidad de cada tarjeta depende de su `id`.
- Migraciones compatibles `016_payment_method_names_scoped_to_parent.sql` y `017_card_names_not_unique.sql`.
- Mensajes de validacion especificos en español e ingles.
- Pruebas de integridad para duplicados permitidos y bloqueados.
- [Notas del hotfix en espanol](docs/v3.6.1-release/notas-v3.6.1.md)
- [Hotfix notes in English](docs/v3.6.1-release/v3.6.1-release-notes.md)

### v3.7.0 - Presupuestos e Informes

Estado: implementado y validado en local.

Objetivo: controlar el gasto mensual esperado frente al gasto real y ampliar el analisis financiero con informes configurables.

Incluye:
- Presupuesto mensual por categoria.
- Acceso principal como `Presupuestos`.
- Gasto real calculado desde todos los movimientos de tipo gasto, independientemente de la cuenta utilizada.
- Barras de consumo y alertas visuales al 80%, 90% y 100%.
- Filtros para categorias en riesgo, excedidas y sin presupuesto.
- Resumen mensual de presupuesto, gasto, disponible y categorias fuera de presupuesto.
- Presupuesto vigente editable únicamente en el mes actual.
- Herencia automática del último presupuesto vigente en los meses siguientes.
- Consulta histórica de solo lectura con el presupuesto aplicado y el gasto real de cada mes.
- Gestión de categorías mantenida como responsabilidad independiente.
- Resumen de presupuesto en el dashboard.
- Comparativas configurables por mes, trimestre y año.
- Evolución de ingresos, gastos, ahorro y balance.
- Comparativas avanzadas entre periodos (MoM/YoY).
- Filtros por categoría, banco, cuenta, tarjeta y préstamo.
- Exportación contextual a CSV y vista preparada para imprimir o guardar como PDF.
- Informes guardados por usuario como configuraciones reutilizables.
- Migraciones `018_category_budgets.sql` a `023_remove_record_source.sql`.

Mas detalles:
- [Notas de release en espanol](docs/v3.7-release/notas-v3.7.0.md)
- [Release notes in English](docs/v3.7-release/v3.7.0-release-notes.md)

### v3.8.0 - Operacion, modulos opcionales e i18n modular

Estado: en desarrollo.

Objetivo: simplificar la operacion de la aplicacion, consolidar las cuentas de ahorro y completar capacidades de configuracion global sin alterar los importes historicos.

Incluye:
- `DATABASE_URL` como unica fuente de configuracion de PostgreSQL.
- Eliminacion del fichero `.app_config.json` y su cifrado asociado.
- Wizard simplificado para crear el primer administrador sobre la BD configurada.
- Eliminacion de la configuracion y el acceso de BD desde Gestion.
- SMTP configurado exclusivamente mediante variables de entorno, sin credenciales persistidas en Gestion ni en la BD.
- Estado SMTP mostrado dentro de Informes sin exponer credenciales.
- Cuentas bancarias clasificadas como corrientes o de ahorro.
- Varias cuentas de ahorro con saldo inicial, aportaciones y gastos asociados.
- Agregado `Savings Accounts` en dashboard e Informes, con desglose por cuenta cuando existe mas de una.
- Gastos contabilizados en presupuesto e informes independientemente de la cuenta utilizada.
- Selector global de moneda en Sistema para cambiar el formato de todos los importes sin convertir los datos existentes.
- Copias PostgreSQL verificadas en formato `.dump`, con integridad SHA-256, carga local y restauracion confirmada con copia preventiva.
- Retencion de copias configurada por dias y planificador interno diario a las 00:00, sin un contenedor cron adicional.
- Cobertura automatizada ampliada para backups, restauraciones, rutas y planificador interno.
- Módulo de préstamos opcional, activable desde `Gestión → Módulos` sin eliminar préstamos, pagos ni historial.
- Navegación, tarjetas del dashboard, filtros y formularios de pago de préstamo ocultos cuando el módulo está desactivado; las rutas de préstamos se bloquean.
- Módulo de presupuestos opcional, activable desde `Gestión → Módulos` sin eliminar la configuración ni el histórico mensual.
- Los dos módulos se configuran con un único formulario y botón Guardar.
- Actualizacion de Compose, version visible, documentacion operativa y migraciones `024` a `029`.

Mas detalles:
- [Notas de release en espanol](docs/v3.8-release/notas-v3.8.0.md)
- [Release notes in English](docs/v3.8-release/v3.8.0-release-notes.md)

### v3.8.1 - Fiabilidad del planificador de copias de seguridad

Estado: completado.

Objetivo: asegurar que una copia programada pendiente no se pierda cuando el planificador interno se reinicia.

Incluye:
- Ejecucion de la copia de seguridad pendiente despues de reiniciar el planificador.
- Ajustes de version a `3.8.1` en la aplicacion, documentacion, plantillas de informes e imagen de produccion.
- Actualizacion de pruebas de presupuestos e informes para mantener estable la suite de regresion.
- [Notas de release en espanol](docs/v3.8-release/notas-v3.8.1.md)
- [Release notes in English](docs/v3.8-release/v3.8.1-release-notes.md)

### v3.9.0 - Importacion de registros bancarios

Estado: implementado y validado en local.

Objetivo: reducir el trabajo manual al registrar movimientos mediante un flujo seguro de carga, revision y confirmacion de extractos bancarios.

Incluye:
- Acceso `Importar registros` integrado en las paginas de Gastos e Ingresos.
- Soporte inicial para extractos de ING en formatos `.xls` y `.xlsx`, con limite de 5 MB y 1.000 registros.
- Lectura de fecha valor, categoria, descripcion e importe; subcategoria, comentario y saldo de ING se ignoran.
- Previsualizacion editable antes de guardar, con concepto, descripcion, categoria, importe y acciones por fila.
- Posibilidad de excluir movimientos individualmente sin importarlos.
- Importacion atomica: si algun registro seleccionado no es valido, no se guarda ninguno.
- Gastos vinculados obligatoriamente a una tarjeta activa existente, comun para toda la importacion.
- Correspondencia de categorias de ING con las categorias existentes y alerta visual cuando requieren asignacion manual.
- Eliminacion automatica de la alerta al seleccionar una categoria valida.
- Normalizacion de conceptos frecuentes: Amazon, AHORRAMAS, Uber, PayPal e iCloud, entre otros.
- Reglas automaticas de categoria para alimentacion, hogar, transporte, salud, ocio y suscripciones.
- Agrupacion mensual automatica de compras de Amazon, conservando un detalle desplegable de los movimientos originales.
- Devoluciones de Amazon descontadas del grupo de gastos del mismo mes y excluidas de la importacion de ingresos.
- Importacion separada de movimientos positivos desde Ingresos.
- Clasificacion visual de movimientos positivos como ingreso, devolucion o transferencia.
- Transferencias desmarcadas por defecto para evitar contabilizarlas accidentalmente como ingresos.
- Ingresos guardados sin categoria ni metodo de pago, de acuerdo con las reglas actuales del modelo de datos.
- Catalogo de endpoints actualizado a 99 rutas y 107 combinaciones endpoint-metodo.
- Cobertura automatizada del flujo de carga, previsualizacion, correspondencias, agrupaciones y confirmacion.

## Ideas futuras

Estas ideas no estan comprometidas todavia y pueden moverse segun prioridad.

### Evolucion de cuentas y transferencias

Objetivo: representar el origen y destino real de los movimientos entre cuentas y ampliar los tipos de cuenta disponibles.

Ideas:
- Registrar el origen de ingresos y aportaciones de ahorro como transferencias desde una cuenta corriente.
- Incorporar cuentas `cash` y `other`.
- Permitir que las cuentas `cash` y `other` no requieran banco.
- Definir como se calcula y presenta el saldo de estos nuevos tipos.

### Evolucion del importador bancario

Objetivo: ampliar el importador de v3.9.0 a mas bancos, formatos y controles preventivos.

Ideas:
- Incorporar extractos CSV.
- Mapeo manual de columnas.
- Deteccion de posibles duplicados.
- Plantillas de formato para nuevos bancos.
- Reglas de concepto y categoria configurables por el usuario.
- Recordar correspondencias manuales para importaciones posteriores.

### Cierre mensual

Objetivo: crear un flujo guiado para revisar y cerrar cada mes.

Navegacion futura: candidato a acceso principal como `Cierre mensual` si se consolida como un flujo recurrente; tambien puede integrarse en Dashboard.

Ideas:
- Checklist de cierre mensual.
- Snapshot mensual de ingresos, gastos, ahorros, prestamos y balance.
- Estado opcional de mes cerrado.
- Comparativa con el mes anterior.
- Notas/resumen del mes.

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
- Notificaciones internas y recordatorios.
- Soporte multi-moneda con conversiones y tipos de cambio historicos.
- API tokens para integraciones externas.
- Metricas operativas basicas: latencias por ruta y tasa de errores.
- Retencion configurable de logs de negocio en base de datos.
- Mejora de rendimiento en listados masivos/exportaciones.
- Scripts y documentacion operativa de mantenimiento.
