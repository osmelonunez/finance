# Finance - Personal Finance Application

![GitHub release (latest by date)](https://img.shields.io/github/v/release/osmelonunez/finance)
![License](https://img.shields.io/github/license/osmelonunez/finance)
![Repo size](https://img.shields.io/github/repo-size/osmelonunez/finance)

Language: English | [Español](./README.es.md)

Finance is a Flask + PostgreSQL web app to manage personal/household finances with role-based access, dashboard analytics, records, backups, and SMTP reports.

This application was created with AI assistance. The project ideas and direction come from the author.

Repository: [osmelonunez/finance](https://github.com/osmelonunez/finance)

## Current Version

- Stable version: `3.0.0`
- Production compose image is pinned to `f1nanc3/finance:3.0.0`

## Core Features

- Separate views: `Expenses`, `Incomes`, `Savings`
- Dashboard with monthly and yearly charts
- Auth with roles: `admin`, `editor`, `user`
- Rate limiting in auth endpoints
- Profile preferences per user:
  - language (`en` / `es`)
  - rows per page
  - email notifications on/off
- Management modules:
  - users
  - database connection
  - backups
  - SMTP + email reports
  - categories
  - system settings
  - accounts/cards
- Deferred and financed expenses
- Localized categories for default list (`en` / `es`)
- SQL migrations with migration tracking table
- Gunicorn runtime in Docker, running as non-root user
- Structured JSON logs + health checks (`/health/live`, `/health/ready`)

## Tech Stack

- Backend: Python, Flask, psycopg2
- Database: PostgreSQL
- Frontend: Jinja2 templates, Bootstrap, Chart.js
- Runtime: Docker, Docker Compose, Gunicorn

## Local Run (Docker)

### Requirements

- Docker + Docker Compose
- PostgreSQL reachable from the container

### Start

```bash
make up
```

App URL:
- [http://localhost:3000](http://localhost:3000)

Useful commands:

```bash
make restart
make logs
make down
```

## First-Time Setup Wizard

On first access, app redirects to `/setup`.

Options:
- `Use existing database`
- `Create new database`

Notes:
- First admin is created from wizard form.
- No hardcoded `admin/admin`.
- Database and database user must already exist.
- DB connection is persisted in `/config/.app_config.json`.
- If `DB_CONFIG_ENCRYPTION_KEY` is configured, DB URL is stored encrypted.

## Production Deploy (Prebuilt Image)

Compose file:
- `/Users/osmel/git/finance/docker/docker-compose.yaml`

Commands:

```bash
make up-prod
make logs-prod
make down-prod
```

## 🐳 Docker Image

- [f1nanc3/finance](https://hub.docker.com/r/f1nanc3/finance)

## Build and Publish

Multi-arch build + push (`linux/amd64,linux/arm64`):

```bash
make build IMAGE=f1nanc3/finance:latest
```

Local build only:

```bash
make build-local
```

Dependency audit:

```bash
make audit-deps
```

## Production Environment Variables (Important)

Required in production:
- `APP_ENV=production`
- `SECRET_KEY` (must be custom, non-default)
- `SMTP_ENCRYPTION_KEY` (must be custom, non-default)
- `DB_CONFIG_ENCRYPTION_KEY` (required when using `/config/.app_config.json` DB config)

Recommended:
- `APP_PUBLIC_URL` (links in emails)
- `SESSION_LIFETIME_HOURS` (default `12`)
- `LOG_FORMAT=json`
- `LOG_LEVEL=INFO`

Rate limits:
- `RATE_LIMIT_LOGIN_IP`
- `RATE_LIMIT_LOGIN_ID`
- `RATE_LIMIT_REGISTER_IP`
- `RATE_LIMIT_PASSWORD_CHANGE`

## Security and Ops Notes

- In production, startup fails if required secrets are missing/default.
- App config file is created with mode `0600`.
- SMTP credentials are encrypted at rest.
- DB URL in app config can be encrypted with `DB_CONFIG_ENCRYPTION_KEY`.
- Container logs are rotated via Compose:
  - `max-size: 10m`
  - `max-file: 7`
- Secrets are redacted from logs (passwords/tokens/URLs with credentials).

## Backups

- Backup files are stored at `/backups` in the container.
- Typical mounts:
  - `./backups -> /backups`
  - `./config -> /config`
- Backup schedule/retention/restore/delete from:
  - `Management -> Backups`

## Email and Reports

- SMTP settings are managed in UI (`Management -> SMTP`).
- Sender display name is configurable.
- Monthly/yearly reports are enabled by default.
- Reports are sent only to users:
  - active
  - with email notifications enabled
- Report template version is configurable (phase 1: `v1`).

## License

This project is licensed under the [MIT License](./LICENSE).
