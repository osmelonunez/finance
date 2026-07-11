# v3.4.0 - Robustez de datos y seguridad de UX

## Objetivo

Hacer Finance mas segura despues del trabajo grande de prestamos y bancos de las versiones v3.2 y v3.3, reforzando validaciones, evitando envios duplicados accidentales y haciendo mas claras las acciones destructivas.

Esta version tambien pule las pantallas de gestion y detalle de prestamos, manteniendo los cambios de base de datos concentrados en una sola migracion.

## Alcance implementado

### 1. Limites de texto y constraints de datos

Los limites de texto quedaron estandarizados en validacion backend, validacion frontend y constraints de base de datos.

Limites finales:
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

Notas de implementacion:
- Los limites compartidos estan en `backend/validators.py`.
- La UI usa `data-maxlength` o `maxlength` donde corresponde.
- La base de datos protege los limites con `014_data_robustness_constraints.sql`.
- Todas las comprobaciones de base de datos de v3.4 se unificaron en `014_data_robustness_constraints.sql` porque las migraciones extra solo existian en el entorno de prueba.

### 2. Envio de formularios mas seguro

Se agrego manejo global de formularios en `frontend/templates/base.html`.

Comportamiento implementado:
- Validacion en vivo de campos obligatorios y maximos de caracteres.
- Los botones de envio se deshabilitan cuando hay errores bloqueantes.
- Los envios validos deshabilitan botones para reducir doble envio accidental.
- El texto del boton cambia segun contexto: Guardando, Creando, Eliminando o Procesando.
- Se soportan botones externos asociados mediante el atributo `form`.
- La validacion funciona con filas editables de tablas, incluyendo bancos y cuentas/tarjetas.

Flujos cubiertos:
- Agregar/editar movimientos.
- Duplicar movimientos.
- Agregar/editar prestamos.
- Registrar uso de prestamo.
- Editar gasto mediante modal de confirmacion.
- Categorias, bancos, cuentas/tarjetas, datos demo y formularios destructivos de gestion.

### 3. Modales de acciones destructivas

Las acciones destructivas usan modales de confirmacion consistentes.

Confirmaciones implementadas:
- Eliminar un movimiento desde detalle.
- Eliminar un uso de prestamo.
- Eliminar un prestamo.
- Eliminar una categoria.
- Eliminar datos demo.
- Eliminar bancos cuando esta permitido.
- Eliminar cuentas/tarjetas cuando esta permitido.

El reset de base de datos mantiene la doble confirmacion existente.

### 4. Auditoria visual

Las vistas de detalle muestran metadatos de auditoria de forma discreta.

Implementado:
- Detalle de movimiento muestra Creado y Ultima edicion.
- Detalle de prestamo muestra Creado y Ultima edicion.
- La etiqueta de actualizacion se dejo como “Ultima edicion” para que refleje mejor el significado en la UI.

### 5. Logs de eventos de negocio

Se amplio y normalizo el logging de acciones de usuario y datos demo.

Areas implementadas:
- Registros: crear, actualizar, duplicar, eliminar.
- Prestamos: crear, actualizar, cambios de estado, eliminar, crear/eliminar uso.
- Categorias: crear, actualizar, eliminar, bloqueo de eliminacion.
- Bancos: crear, actualizar, eliminar, bloqueo de eliminacion.
- Metodos de pago: crear, actualizar, eliminar, bloqueo de eliminacion.
- Datos demo: insertar y eliminar.

Los logs de datos demo ahora incluyen el prefijo `[DEMO DATA]` y conteos por entidad, para que el seed funcione tambien como una prueba visible.

### 6. Seguridad de prestamos y analiticas

Implementado:
- Los prestamos marcados como Pagado o Cancelado se excluyen automaticamente de analiticas.
- El prestamo demo pagado queda excluido de analiticas.
- Los pagos e historial existentes se mantienen aunque la exclusion este activa.
- Se reforzo la validacion del uso de prestamos.
- Los avisos de campos obligatorios en uso de prestamos ya no desalinean el formulario.
- La fecha de inicio al editar un prestamo usa el mismo selector mensual que al crearlo.
- Al cambiar la fecha de inicio se mantiene el recalculo de plazos que ya venia de v3.3.

### 7. Pulido de Gestion

La gestion de metodos de pago se reorganizo.

Implementado:
- La pantalla se separa en Bancos, Cuentas y Tarjetas.
- Cuentas y Tarjetas tienen formularios de alta separados.
- El tipo ya no se selecciona manualmente; lo determina la seccion.
- Bancos se edita con el mismo patron de acciones que cuentas/tarjetas: Editar, Cancelar, Guardar, Eliminar.
- Eliminar banco se bloquea si esta usado por cuentas/tarjetas o prestamos.
- Los avisos de campos obligatorios en gestion quedan dentro de su panel y no rompen la alineacion.
- La validacion de tablas editables soporta controles asociados por `form`.

### 8. Documentacion y versionado

Implementado:
- Version subida a `3.4.0`.
- README y README.es actualizados con la nueva version estable.
- Roadmap actualizado con v3.4 y enlaces a estos detalles.
- Las notas de v3.4 se movieron de `local-notes` a `docs/v3.4-planning` para quedar dentro de la documentacion del proyecto.

## Migracion

Migracion de la version:
- `014_data_robustness_constraints.sql`

Objetivo:
- Agrega constraints de base de datos para los limites finales de texto.
- Usa constraints `NOT VALID` para que una base existente pueda aplicar la migracion sin validar inmediatamente registros historicos.

## Validacion realizada

Repetido durante la implementacion:
- `python3 -m compileall backend`
- `git diff --check`
- `make up`
- Revision de logs de arranque del contenedor.
- Render de templates modificados cuando aportaba valor.

Flujos probados durante la version:
- Validacion de limites de texto.
- Comportamiento anti doble envio.
- Modales de confirmacion destructiva.
- Crear/editar/eliminar categorias.
- Gestion de bancos, cuentas y tarjetas.
- Detalle de prestamo, uso de prestamo y edicion de prestamos.
- Logs al insertar/eliminar datos demo.

## Fuera de alcance

Queda para versiones posteriores:
- Importador CSV bancario.
- Presupuestos por categoria.
- Flujo de cierre mensual.
- Reportes PDF.
- Adjuntos.
- Ejecucion de datos demo completamente mediante endpoints.

## Nombre de release

Nombre final:
- `v3.4.0 - Robustez de datos y seguridad de UX`
