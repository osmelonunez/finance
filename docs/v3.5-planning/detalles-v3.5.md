# v3.5.0 - Cuentas y tarjetas 2.0

## Objetivo

Convertir las cuentas y tarjetas en entidades consultables y seguras, conectando su gestión con los movimientos y los bancos sin cambiar el esquema de base de datos.

## Navegación

- Cuentas, tarjetas y bancos salen de Gestión y disponen de un espacio propio en `/payment-methods`.
- La navegación interna se divide en `KPI`, `Relaciones`, `Bancos`, `Cuentas` y `Tarjetas`.
- `/payment-methods` abre el KPI por defecto.
- Las antiguas rutas bajo `/management/payment-methods` y las rutas renombradas redirigen a sus destinos actuales.

## Gestión e integridad

- La eliminación se bloquea explícitamente cuando existen movimientos asociados.
- La protección de clave foránea existente se mantiene como segunda barrera.
- Una cuenta o tarjeta nueva solo puede vincularse a un banco activo.
- La relación con un banco también es obligatoria al editar una cuenta o tarjeta.
- Una cuenta o tarjeta no puede activarse si su banco está inactivo.
- Al desactivar un banco, sus cuentas y tarjetas se desactivan automáticamente.
- Las altas y duplicados de movimientos solo aceptan cuentas/tarjetas activas.
- La edición conserva una cuenta/tarjeta inactiva ya utilizada, pero no permite asignar otra inactiva.
- Un único formulario contextual permite crear un banco, una cuenta o una tarjeta y dirige el alta a la sección correspondiente.

## Detalles e historial

El detalle de cuenta o tarjeta muestra:

- tipo, estado, banco y referencia;
- gasto total acumulado;
- gasto del mes actual;
- número de movimientos asociados;
- movimientos paginados en bloques de diez, cargados desde el servidor al cambiar de página;
- acceso directo al listado de gastos filtrado.

El detalle de banco muestra sus KPI, cuentas, tarjetas y el mismo historial paginado de movimientos.

Las pestañas `KPI`, `Relaciones`, `Bancos`, `Cuentas` y `Tarjetas` permanecen visibles en todas las vistas de detalle.

## Filtros, KPI y relaciones

- El listado de gastos incorpora filtros independientes por banco, cuenta y tarjeta.
- Los filtros incluyen entidades inactivas para poder consultar el histórico.
- El KPI muestra conteos de bancos, cuentas y tarjetas activas, además del gasto del mes actual.
- El resumen financiero permite cambiar entre bancos, cuentas y tarjetas y seleccionar el ejercicio anual.
- Se muestran gráficas separadas de gasto mensual, anual y total, más una gráfica comparativa con los tres valores.
- Cada gráfica presenta un mensaje claro cuando no existen gastos para el ámbito y periodo seleccionados.
- La vista `Relaciones` agrupa cuentas y tarjetas bajo su banco y ordena primero los bancos con más elementos vinculados.
- La antigua tabla de resumen bancario se eliminó para evitar duplicar los KPI y las gráficas.

## Presentación de importes

- Los importes y números grandes se agrupan según el idioma activo.
- Las gráficas utilizan el mismo formato monetario en ejes, etiquetas y tooltips.

## Base de datos

No requiere migración. Se utilizan las relaciones e índices existentes sobre `payment_methods`, `banks` y `records`.

## Despliegue

- Versión de aplicación: `3.5.0`.
- Imagen de producción: `f1nanc3/finance:3.5.0`.
- Tag Git previsto: `v3.5.0`.

## Validación realizada

- Compilación completa de Python.
- Carga de todas las plantillas Jinja.
- Validación de Docker Compose.
- Pruebas autenticadas de rutas de navegación, detalle, KPI y filtros.
- Pruebas de integridad y estado activo/inactivo.
- Validación del selector de año, cambio de ámbito, estados vacíos y formato monetario de las gráficas.
- Health checks del contenedor de desarrollo.
