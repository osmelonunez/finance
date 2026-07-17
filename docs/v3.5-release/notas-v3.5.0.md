# Finance v3.5.0 - Cuentas y tarjetas 2.0

## Resumen

Esta versión convierte bancos, cuentas y tarjetas en un espacio funcional independiente, con indicadores financieros, relaciones entre entidades, vistas de detalle e historial de movimientos. También refuerza la integridad de los datos y mejora la lectura de importes en toda la aplicación.

## Cuentas y tarjetas

- Nuevo espacio principal `Cuentas y tarjetas` en `/payment-methods`, separado de Gestión.
- Navegación interna mediante `KPI`, `Relaciones`, `Bancos`, `Cuentas` y `Tarjetas`.
- Formulario único y contextual para crear bancos, cuentas o tarjetas.
- Banco obligatorio al crear o editar una cuenta o tarjeta.
- Solo se pueden asociar cuentas y tarjetas a bancos activos.
- Desactivación automática de las cuentas y tarjetas al desactivar su banco.
- Bloqueo de eliminación de cuentas o tarjetas con movimientos asociados.
- Compatibilidad mediante redirecciones desde las rutas anteriores de Gestión.

## KPI y relaciones

- Indicadores de bancos, cuentas y tarjetas activas y del gasto mensual.
- Resumen financiero seleccionable por banco, cuenta o tarjeta.
- Selector de año para consultar ejercicios anteriores.
- Gráficas de gasto mensual, anual, total y comparativa.
- Estados vacíos claros cuando no existen gastos para el ámbito seleccionado.
- Vista `Relaciones` ordenada por el número de cuentas y tarjetas vinculadas a cada banco.

## Detalles e historial

- Nuevas vistas de detalle para bancos, cuentas y tarjetas.
- Métricas de gasto mensual, anual y total, según corresponda.
- Banco asociado, estado, referencia y número de movimientos.
- Historial de movimientos paginado en bloques de diez y cargado desde el servidor al cambiar de página.
- Acceso directo al listado de gastos filtrado por la entidad consultada.
- Navegación de Cuentas y tarjetas disponible dentro de todas las vistas de detalle.

## Gastos y presentación

- Filtros independientes de gastos por banco, cuenta y tarjeta.
- Entidades inactivas disponibles en los filtros para conservar el acceso al histórico.
- Altas y duplicados de movimientos limitados a cuentas y tarjetas activas.
- Formato monetario y numérico localizado en toda la aplicación.
- Agrupación de miles adaptada al idioma en tablas, indicadores, ejes, etiquetas y tooltips.

## Compatibilidad

- No requiere migración de base de datos.
- No modifica ni elimina los datos existentes.
- Mantiene compatibilidad con las rutas anteriores mediante redirecciones.
- El compose de producción expone el servicio en el puerto `5000`.

## Despliegue

- Imagen: `f1nanc3/finance:3.5.0`
- Imagen flotante: `f1nanc3/finance:latest`
- Tag Git: `v3.5.0`
- Nombre de la release: `Finance v3.5.0`

## Validación

- Compilación de Python y carga de plantillas Jinja.
- Validación del Docker Compose de producción.
- Construcción y arranque de la imagen de producción.
- Comprobación de health checks y conexión a la base de datos.
- Revisión manual de navegación, permisos, integridad, filtros, paginación, estados vacíos y ambos idiomas.
- Suite automática de regresión con inventario de rutas, comprobación de métodos, autenticación, roles, CSRF y flujos CRUD sobre PostgreSQL aislado.
- Resultado de referencia: 275 pruebas superadas y 69% de cobertura, con un mínimo obligatorio del 65%.
