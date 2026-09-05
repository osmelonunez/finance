# Finance - Aplicación de Finanzas Personales

![GitHub release (latest by date)](https://img.shields.io/github/v/release/osmelonunez/finance)
![License](https://img.shields.io/github/license/osmelonunez/finance)
![Repo size](https://img.shields.io/github/repo-size/osmelonunez/finance)

Idioma: Español | [English](./README.md)

Finance es una aplicación web Flask + PostgreSQL para gestionar finanzas personales/familiares con control por roles, dashboard, registros, copias de seguridad y reportes por correo.

Esta aplicación se creó con ayuda de IA. Las ideas y la dirección del proyecto son del autor.

Repositorio: [osmelonunez/finance](https://github.com/osmelonunez/finance)

## Versión Actual

- Versión actual: `3.9.0`
- Release: `v3.9.0 - Importación de registros bancarios`
- El compose de producción está preparado para `f1nanc3/finance:3.9.0`
- [Notas de la versión 3.9.0](docs/v3.9-release/notas-v3.9.0.md)

## Funcionalidades Principales

- Vistas separadas: `Panel`, `Gastos`, `Ingresos`, `Ahorros`, `Informes`, `Banca` y `Gestión`; `Presupuestos` y `Préstamos` son módulos opcionales.
- Dashboard con gráficas mensuales y anuales, además de indicadores de deuda de préstamos y resumen de presupuesto cuando sus módulos están activos.
- Presupuestos vigentes por categoría, editables en el mes actual y heredados automáticamente en los meses siguientes
- Histórico mensual de solo lectura con presupuesto aplicado, gasto real, desviación y alertas al 80%, 90% y 100%
- Informes mensuales y anuales en pantalla con resumen, gasto por categoría y principales gastos
- Comparativas por mes, trimestre y año entre dos desplegables basados en la ventana de años de Finance
- Gráfico de evolución financiera para 6 meses, 12 meses o la ventana de años, con series activables
- Selector unificado de comparativas Libre, MoM y YoY con desglose por categoría y mayores aumentos/reducciones
- Filtros compartidos por categoría, banco, cuenta, tarjeta y préstamo, exportación CSV y vista de impresión/PDF
- Informes guardados por usuario con periodos, modos y filtros reutilizables
- Configuración de reportes, estado SMTP e historial de entregas integrados en Informes
- Navegación interna de Informes separada en Resumen, Envío por correo y Plantillas de correo
- Autenticación con roles: `admin`, `editor`, `user`
- Rate limiting en endpoints de autenticación
- Preferencias por usuario:
  - idioma (`en` / `es`)
  - filas por página
  - notificaciones por correo on/off
- Módulos de Gestión:
  - usuarios
  - copias de seguridad
  - categorías
  - ajustes del sistema
  - módulos opcionales (`Préstamos` y `Presupuestos`), gestionados conjuntamente por administradores desde `Gestión -> Módulos`
- Espacio independiente `Banca` en `/payment-methods`:
  - panel KPI con selectores de banco/cuenta/tarjeta y año
  - gráficas de gasto mensual, anual, total y comparativa
  - vista de relaciones Banco → Cuenta → Tarjeta con conexiones directas entre cada cuenta y sus tarjetas
  - pestañas separadas para gestionar bancos, cuentas y tarjetas
  - un único formulario contextual para crear bancos, cuentas o tarjetas
- Detalle de bancos, cuentas y tarjetas con totales de gasto y paginación de movimientos en servidor
- El detalle de banco muestra sus préstamos asociados y KPI de capital, deuda pendiente, importe amortizado y cuota mensual cuando Préstamos está activo
- El gasto bancario incluye los pagos de préstamos (capital e intereses); los usos del capital son informativos y no se consideran gasto propio ni saldo disponible
- Filtros de gastos específicos por banco, cuenta y tarjeta
- Las cuentas requieren un banco y las tarjetas requieren una cuenta; no pueden eliminarse mientras tengan datos relacionados
- Los nombres de cuenta pueden repetirse entre bancos distintos; los nombres de tarjeta pueden repetirse porque las tarjetas se identifican por ID
- Formato monetario y numérico adaptado al idioma en toda la aplicación
- Préstamos con banco, cantidad, plazo, cuota mensual, descripción, estado y seguimiento de pagos
- Tipos de préstamo: sin intereses, con intereses e hipotecas con separación de amortización/intereses
- Seguimiento editable de usos de préstamo para registrar en qué se gasta el dinero prestado sin contarlo como ingreso mensual
- Pagos de préstamo registrados desde gastos sin contar la solicitud del préstamo como ingreso
- Exclusión opcional de préstamos en dashboard y totales de analíticas
- Los módulos opcionales Préstamos y Presupuestos conservan todos sus datos e histórico al desactivarse; navegación, contenido relacionado del dashboard, filtros, formularios y rutas se ocultan o bloquean según corresponda.
- Pagos aplazados
- Categorías por defecto localizadas (`en` / `es`)
- Migraciones SQL con tabla de control
- Runtime con Gunicorn en Docker, ejecutando como usuario no root
- Logs JSON estructurados + health checks (`/health/live`, `/health/ready`)
- Optimización de consultas de dashboard + caché corto (30s) con invalidación en cambios de datos
- Diez plantillas versionadas de reportes (`v1` a `v10`) en una cuadrícula única de cinco por fila para mensual y anual
- Branding compartido para emails con nombre, cabecera y pie centrado
- Catálogos de traducción modulares: los textos de nuevos módulos viven en `backend/locales/` y se mantiene compatible la API existente de `i18n.py`.

## Informes y analítica

El espacio `Informes` reúne el análisis financiero y la entrega por correo:

- Resúmenes mensuales y anuales de ingresos, gastos, ahorro y balance.
- Comparaciones libres, MoM y YoY por mes, trimestre o año, con variación absoluta, porcentual y desglose por categoría.
- Evolución financiera para los últimos 6 o 12 meses y para varios años, con series que se pueden activar u ocultar.
- Filtros compartidos por categoría, banco, cuenta, tarjeta y préstamo (cuando Préstamos está activo).
- Exportación contextual a CSV y una presentación específica para imprimir o guardar como PDF.
- Informes guardados por usuario que conservan periodos, modo de comparación, métricas y filtros.
- Configuración de reportes por correo, historial de entregas y diez plantillas con vista previa mensual o anual.
- Cuentas corrientes y de ahorro, con saldo inicial individual y agregado consolidado `Savings Accounts`.
- Las aportaciones de ahorro exigen una cuenta de destino; los gastos y tarjetas vinculados descuentan de esa cuenta.

## Capturas de Pantalla

Consulta la [carpeta de capturas](docs/screenshots/) para ver las vistas actuales de la aplicación.

## Stack Tecnológico

- Backend: Python, Flask, psycopg2
- Base de datos: PostgreSQL
- Frontend: plantillas Jinja2, Bootstrap, Chart.js
- Runtime: Docker, Docker Compose, Gunicorn

## Ejecución Local (Docker)

### Requisitos

- Docker + Docker Compose
- PostgreSQL accesible desde el contenedor

### Inicio

```bash
make up
```

URL de la app:
- [http://localhost:3000](http://localhost:3000)

Comandos útiles:

```bash
make restart
make logs
make down
```

La URL de la base de datos de desarrollo se mantiene fuera de Git en:

```text
tools/docker/docker-compose.override.yaml
```

Créalo localmente con:

```yaml
services:
  finance:
    environment:
      DATABASE_URL: "postgresql://usuario:contraseña@servidor-bd:5432/finance_dev"
      SMTP_ENABLED: "true"
      SMTP_HOST: "smtp.example.com"
      SMTP_PORT: "587"
      SMTP_USER: "finance@example.com"
      SMTP_PASSWORD: "CHANGE_ME"
      SMTP_USE_TLS: "true"
      SMTP_FROM_EMAIL: "finance@example.com"
      SMTP_SENDER_NAME: "Finance"
```

Este override está ignorado por Git. El `Makefile` lo combina automáticamente
con `tools/docker/docker-compose.yaml`.

## Wizard de Inicialización

En el primer acceso, la aplicación ejecuta las migraciones contra la `DATABASE_URL` configurada en Docker Compose y redirige a `/setup`.

Notas:
- El primer admin se crea desde el formulario del wizard.
- No existe `admin/admin` por defecto.
- La BD y su usuario deben existir previamente y ser accesibles mediante `DATABASE_URL`.
- El wizard puede validar la conexión configurada, pero nunca lee ni guarda credenciales de BD.

## Despliegue en Producción (Imagen precompilada)

Fichero compose:
- `docker/docker-compose.yaml`

Comandos:

```bash
make up-prod
make logs-prod
make down-prod
```

## 🐳 Imagen Docker

- [f1nanc3/finance](https://hub.docker.com/r/f1nanc3/finance)

## Build y Publicación

Build multi-arquitectura + push (`linux/amd64,linux/arm64`):

```bash
make build
```

Build local (`f1nanc3/finance:latest`):

```bash
make build-local
```

Auditoría de dependencias:

```bash
make audit-deps
```

## Pruebas automáticas

Las pruebas se ejecutan en contenedores aislados y utilizan una base PostgreSQL temporal llamada `finance_test`. La suite rechaza cualquier `DATABASE_URL` cuyo nombre de base de datos no termine en `_test`.

```bash
make test-unit      # validadores y formato numérico
make test-routes    # rutas, métodos, autenticación, permisos y CSRF
make test-release   # suite completa con informe de cobertura
make test-endpoints # regenerar el catálogo Markdown de endpoints
make test-clean     # limpieza manual del entorno de pruebas
```

El inventario se obtiene directamente de Flask. Cada ruta nueva se incorpora al barrido y cualquier endpoint POST nuevo debe declarar explícitamente su payload de prueba.

- Catálogo versionado: [`docs/testing/endpoints.md`](docs/testing/endpoints.md).
- Informe más reciente: `test-reports/latest.md`.
- Histórico local: `test-reports/finance-test-report-YYYYMMDD-HHMMSS.md`.

## Variables Importantes para Producción

Obligatorias en producción:
- `APP_ENV=production`
- `DATABASE_URL` (cadena única de conexión PostgreSQL)
- `SECRET_KEY` (valor propio, no default)

Recomendadas:
- `APP_PUBLIC_URL` (enlaces en correos)
- `SESSION_LIFETIME_HOURS` (por defecto `12`)
- `LOG_FORMAT=text` para logs coloreados en contenedor, o `json` para logs estructurados
- `LOG_COLOR=true` para colorear logs de texto por nivel (`INFO` verde, `WARNING` amarillo, `ERROR` rojo)
- `LOG_LEVEL=INFO`

Rate limits:
- `RATE_LIMIT_LOGIN_IP`
- `RATE_LIMIT_LOGIN_ID`
- `RATE_LIMIT_REGISTER_IP`
- `RATE_LIMIT_PASSWORD_CHANGE`

## Notas de Seguridad y Operación

- En producción, el arranque falla si faltan secretos obligatorios o si están en default.
- Las credenciales SMTP y de BD permanecen fuera de la aplicación, en variables de entorno o secretos.
- Las credenciales de BD permanecen fuera de la aplicación en `DATABASE_URL`.
- Los logs del contenedor rotan por compose:
  - `max-size: 10m`
  - `max-file: 7`
- Los logs redaccionan secretos (passwords/tokens/URLs con credenciales).

## Copias de Seguridad

- Las copias se guardan en `/backups` dentro del contenedor.
- Montajes típicos:
  - `./backups -> /backups`
- Las copias usan el formato personalizado `.dump` de PostgreSQL y se verifican al crearlas o cargarlas.
- Un programador interno del mismo contenedor ejecuta la tarea configurada a las `00:00` (`TZ`, por defecto `Europe/Madrid`); no hace falta otro contenedor cron.
- La retención conserva las copias creadas dentro del número de días configurado.
- Restaurar exige confirmar el nombre del archivo y crea una copia preventiva justo antes.
- Gestión (programación, retención, carga, restauración, eliminación):
  - `Management -> Backups`

## Correo y Reportes

- SMTP se configura mediante `SMTP_ENABLED`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`,
  `SMTP_PASSWORD`, `SMTP_USE_TLS`, `SMTP_FROM_EMAIL` y `SMTP_SENDER_NAME`.
- Informes muestra si SMTP está preparado sin exponer credenciales.
- Reportes mensual/anual activos por defecto.
- Los correos se envían solo a usuarios:
  - activos
  - con notificaciones por correo activadas
- Plantilla mensual y anual configurables entre diez estilos, incluidos Editorial, Panel, Recibo, Estado financiero, Magazine, Minimalista y Neón, con vista previa usando datos reales y branding compartido.

## Licencia

Este proyecto está bajo la [MIT License](./LICENSE).
