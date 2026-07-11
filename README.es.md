# Finance - Aplicación de Finanzas Personales

![GitHub release (latest by date)](https://img.shields.io/github/v/release/osmelonunez/finance)
![License](https://img.shields.io/github/license/osmelonunez/finance)
![Repo size](https://img.shields.io/github/repo-size/osmelonunez/finance)

Idioma: Español | [English](./README.md)

Finance es una aplicación web Flask + PostgreSQL para gestionar finanzas personales/familiares con control por roles, dashboard, registros, copias de seguridad y reportes por correo.

Esta aplicación se creó con ayuda de IA. Las ideas y la dirección del proyecto son del autor.

Repositorio: [osmelonunez/finance](https://github.com/osmelonunez/finance)

## Versión Actual

- Versión estable: `3.4.0`
- Release: `v3.4.0 - Robustez de datos y seguridad de UX`
- El compose de producción usa imagen fijada en `f1nanc3/finance:3.4.0`

## Funcionalidades Principales

- Vistas separadas: `Panel`, `Gastos`, `Ingresos`, `Ahorros`, `Préstamos`, `Gestión`
- Dashboard con gráficas mensuales y anuales, incluyendo indicadores de deuda de préstamos
- Autenticación con roles: `admin`, `editor`, `user`
- Rate limiting en endpoints de autenticación
- Preferencias por usuario:
  - idioma (`en` / `es`)
  - filas por página
  - notificaciones por correo on/off
- Módulos de Management:
  - usuarios
  - conexión a base de datos
  - copias de seguridad
  - SMTP + reportes por correo
  - categorías
  - ajustes del sistema
  - cuentas
  - tarjetas
  - bancos
- Préstamos con banco, cantidad, plazo, cuota mensual, descripción, estado y seguimiento de pagos
- Tipos de préstamo: sin intereses, con intereses e hipotecas con separación de amortización/intereses
- Seguimiento de uso de préstamo para registrar en qué se gasta el dinero prestado sin contarlo como ingreso mensual
- Pagos de préstamo registrados desde gastos sin contar la solicitud del préstamo como ingreso
- Exclusión opcional de préstamos en dashboard y totales de analíticas
- Pagos aplazados
- Categorías por defecto localizadas (`en` / `es`)
- Migraciones SQL con tabla de control
- Runtime con Gunicorn en Docker, ejecutando como usuario no root
- Logs JSON estructurados + health checks (`/health/live`, `/health/ready`)
- Optimización de consultas de dashboard + caché corto (30s) con invalidación en cambios de datos
- Capa versionada de plantillas de reportes (`v1`) y módulo común de validaciones

## Capturas de Pantalla

### Panel
![Dashboard](docs/screenshots/dashboard.png)

### Gastos
![Expenses](docs/screenshots/expenses.png)

### Préstamos
![Loans](docs/screenshots/loans.png)

### Detalle de préstamo
![Loan Detail](docs/screenshots/loan-detail.png)

### Gestión
![Management](docs/screenshots/management.png)

### Perfil
![Profile](docs/screenshots/profile.png)

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

## Wizard de Inicialización

En el primer acceso, la app redirige a `/setup`.

Opciones:
- `Use existing database`
- `Create new database`

Notas:
- El primer admin se crea desde el formulario del wizard.
- No existe `admin/admin` por defecto.
- La BD y el usuario de BD deben existir previamente.
- La conexión de BD se guarda en `/config/.app_config.json`.
- Si se configura `DB_CONFIG_ENCRYPTION_KEY`, se guarda cifrada.

## Despliegue en Producción (Imagen precompilada)

Fichero compose:
- `/Users/osmel/git/finance/docker/docker-compose.yaml`

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

## Variables Importantes para Producción

Obligatorias en producción:
- `APP_ENV=production`
- `SECRET_KEY` (valor propio, no default)
- `SMTP_ENCRYPTION_KEY` (valor propio, no default)
- `DB_CONFIG_ENCRYPTION_KEY` (obligatoria si se usa configuración de BD en `/config/.app_config.json`)

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
- El fichero de configuración se crea con permisos `0600`.
- Las credenciales SMTP se guardan cifradas.
- La URL de BD en config puede guardarse cifrada con `DB_CONFIG_ENCRYPTION_KEY`.
- Los logs del contenedor rotan por compose:
  - `max-size: 10m`
  - `max-file: 7`
- Los logs redaccionan secretos (passwords/tokens/URLs con credenciales).

## Copias de Seguridad

- Las copias se guardan en `/backups` dentro del contenedor.
- Montajes típicos:
  - `./backups -> /backups`
  - `./config -> /config`
- Gestión (programación, retención, restauración, eliminación):
  - `Management -> Backups`

## Correo y Reportes

- SMTP se configura desde UI (`Management -> SMTP`).
- El nombre visible del remitente es configurable.
- Reportes mensual/anual activos por defecto.
- Los correos se envían solo a usuarios:
  - activos
  - con notificaciones por correo activadas
- Versión de plantilla configurable (fase 1: `v1`).

## Licencia

Este proyecto está bajo la [MIT License](./LICENSE).
