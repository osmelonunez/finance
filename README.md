# Finance - Personal Finance Application

![GitHub release (latest by date)](https://img.shields.io/github/v/release/osmelonunez/finance)
![License](https://img.shields.io/github/license/osmelonunez/finance)
![Repo size](https://img.shields.io/github/repo-size/osmelonunez/finance)

Language: English | [Español](./README.es.md)

Finance is a Flask + PostgreSQL web app to manage personal/household finances with role-based access, dashboard analytics, records, backups, and SMTP reports.

This application was created with AI assistance. The project ideas and direction come from the author.

Repository: [osmelonunez/finance](https://github.com/osmelonunez/finance)

## Current Version

- Current version: `3.8.1`
- Release: `v3.8.1 - Backup scheduler reliability`
- Production compose is prepared for `f1nanc3/finance:3.8.1`
- [v3.8.1 release notes](docs/v3.8-release/v3.8.1-release-notes.md)

## Core Features

- Separate views: `Dashboard`, `Expenses`, `Incomes`, `Savings`, `Reports`, `Banking`, and `Management`; `Budgets` and `Loans` are optional modules.
- Dashboard with monthly and yearly charts, plus loan debt indicators and a budget summary when their respective modules are enabled.
- Effective category budgets editable in the current month and automatically inherited by subsequent months
- Read-only monthly history with applied budget, actual spending, variance, and alerts at 80%, 90%, and 100%
- On-screen monthly and yearly reports with summary, category spending, and top expenses
- Month, quarter and year comparisons using two dropdowns based on Finance's configured year window
- Financial evolution chart for 6 months, 12 months or the configured year window, with toggleable series
- Unified Free, MoM and YoY comparison selector with category breakdown and largest increases/decreases
- Shared category, bank, account, card and loan filters, CSV export and a print/PDF view
- Per-user saved reports with reusable periods, modes and filters
- Email report settings, SMTP status and delivery history integrated into Reports
- Reports sub-navigation separates Summary, Email delivery and Email templates
- Auth with roles: `admin`, `editor`, `user`
- Rate limiting in auth endpoints
- Profile preferences per user:
  - language (`en` / `es`)
  - rows per page
  - email notifications on/off
- Management modules:
  - users
  - backups
  - categories
  - system settings
  - optional modules (`Loans` and `Budgets`), managed together by administrators from `Management -> Modules`
- Top-level `Banking` workspace at `/payment-methods`:
  - KPI dashboard with bank/account/card and year selectors
  - monthly, annual, total, and combined spending charts
  - bank-to-account-to-card relationship view with direct account/card connectors
  - separate bank, account, and card management tabs
  - one contextual form for creating banks, accounts, or cards
- Bank, account, and card detail views with spending totals and server-side movement pagination
- Bank details include associated loans and principal, outstanding debt, amortized amount, and monthly-payment KPIs when Loans is enabled
- Bank spending includes loan payments (principal and interest), while loan capital usages remain informational and are not treated as personal spending or available balance
- Dedicated expense filters for bank, account, and card
- Accounts require a bank and cards require an account; deletion is blocked while related data exists
- Account names may be reused across different banks; card names may be repeated because cards are identified by ID
- Locale-aware number and monetary formatting across the application
- Loans with bank, amount, term, monthly payment, description, status, and payment tracking
- Loan types: no interest, interest-bearing loans, and mortgages with principal/interest split
- Editable loan usage tracking to record what borrowed money is spent on without counting it as monthly income
- Loan payments registered from expenses without counting loan requests as income
- Optional loan exclusion from dashboard and analytics totals
- Optional Loans and Budgets modules preserve all data and history while disabled; navigation, related dashboard content, filters, forms, and routes are hidden or blocked as appropriate.
- Deferred expenses
- Localized categories for default list (`en` / `es`)
- SQL migrations with migration tracking table
- Gunicorn runtime in Docker, running as non-root user
- Structured JSON logs + health checks (`/health/live`, `/health/ready`)
- Dashboard query optimization + short cache (30s) with invalidation on data changes
- Ten versioned report templates (`v1` through `v10`) in one five-column monthly/yearly grid
- Shared email branding with brand name, header and centered footer
- Modular translation catalogues: new module strings live under `backend/locales/` while the existing `i18n.py` API remains compatible.

## Reports and analytics

The `Reports` workspace brings financial analysis and email delivery together:

- Monthly and yearly summaries for income, expenses, savings, and balance.
- Free, MoM, and YoY comparisons by month, quarter, or year, including absolute and percentage changes and category breakdowns.
- Financial evolution across the latest 6 or 12 months or multiple years, with individually selectable series.
- Shared filters for category, bank, account, card, and loan (when Loans is enabled).
- Contextual CSV export and a dedicated print layout that can be saved as PDF.
- Per-user saved reports that preserve periods, comparison mode, metrics, and filters.
- Email report settings, delivery history, and ten templates with monthly or yearly previews.
- Current and savings accounts, with per-account opening balances and a consolidated `Savings Accounts` total.
- Saving contributions require a destination account; linked expenses and cards reduce that account's balance.

## Screenshots

Browse the [screenshots folder](docs/screenshots/) for the current application views.

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

The development database URL is kept outside Git in:

```text
tools/docker/docker-compose.override.yaml
```

Create it locally with:

```yaml
services:
  finance:
    environment:
      DATABASE_URL: "postgresql://user:password@database-host:5432/finance_dev"
      SMTP_ENABLED: "true"
      SMTP_HOST: "smtp.example.com"
      SMTP_PORT: "587"
      SMTP_USER: "finance@example.com"
      SMTP_PASSWORD: "CHANGE_ME"
      SMTP_USE_TLS: "true"
      SMTP_FROM_EMAIL: "finance@example.com"
      SMTP_SENDER_NAME: "Finance"
```

This override is ignored by Git. The `Makefile` automatically combines it with
`tools/docker/docker-compose.yaml`.

## First-Time Setup Wizard

On first access, the app runs migrations against the `DATABASE_URL` configured in Docker Compose and redirects to `/setup`.

Notes:
- First admin is created from wizard form.
- No hardcoded `admin/admin`.
- Database and database user must already exist and be reachable through `DATABASE_URL`.
- The wizard can validate the configured connection but never reads or stores database credentials.

## Production Deploy (Prebuilt Image)

Compose file:
- `docker/docker-compose.yaml`

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
make build
```

Local build only (`f1nanc3/finance:latest`):

```bash
make build-local
```

Dependency audit:

```bash
make audit-deps
```

## Automated tests

Tests run in isolated containers and use a temporary PostgreSQL database named `finance_test`. The suite rejects any `DATABASE_URL` whose database name does not end in `_test`.

```bash
make test-unit      # validators and numeric formatting
make test-routes    # routes, methods, authentication, permissions, and CSRF
make test-release   # complete suite with a coverage report
make test-endpoints # regenerate the Markdown endpoint catalog
make test-clean     # manually clean the test environment
```

The route inventory is read directly from Flask. Every new route is included in the sweep, and every new POST endpoint must explicitly declare its test payload.

- Versioned catalog: [`docs/testing/endpoints.md`](docs/testing/endpoints.md).
- Latest report: `test-reports/latest.md`.
- Local history: `test-reports/finance-test-report-YYYYMMDD-HHMMSS.md`.

## Production Environment Variables (Important)

Required in production:
- `APP_ENV=production`
- `DATABASE_URL` (single PostgreSQL connection string)
- `SECRET_KEY` (must be custom, non-default)

Recommended:
- `APP_PUBLIC_URL` (links in emails)
- `SESSION_LIFETIME_HOURS` (default `12`)
- `LOG_FORMAT=text` for colored container logs, or `json` for structured logs
- `LOG_COLOR=true` to color text logs by level (`INFO` green, `WARNING` yellow, `ERROR` red)
- `LOG_LEVEL=INFO`

Rate limits:
- `RATE_LIMIT_LOGIN_IP`
- `RATE_LIMIT_LOGIN_ID`
- `RATE_LIMIT_REGISTER_IP`
- `RATE_LIMIT_PASSWORD_CHANGE`

## Security and Ops Notes

- In production, startup fails if required secrets are missing/default.
- SMTP and database credentials remain outside the application in environment variables or secrets.
- Database credentials remain outside the application in `DATABASE_URL`.
- Container logs are rotated via Compose:
  - `max-size: 10m`
  - `max-file: 7`
- Secrets are redacted from logs (passwords/tokens/URLs with credentials).

## Backups

- Backup files are stored at `/backups` in the container.
- Typical mounts:
  - `./backups -> /backups`
- Backups use PostgreSQL custom `.dump` format and are verified when created or uploaded.
- An internal scheduler in the same application container runs the configured job at `00:00` (`TZ`, default `Europe/Madrid`); no extra cron container is required.
- Retention keeps backups created within the configured number of days.
- Restore requires an explicit filename confirmation and creates a safety backup immediately beforehand.
- Backup schedule/retention/upload/restore/delete from:
  - `Management -> Backups`

## Email and Reports

- SMTP settings are supplied through `SMTP_ENABLED`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`,
  `SMTP_PASSWORD`, `SMTP_USE_TLS`, `SMTP_FROM_EMAIL`, and `SMTP_SENDER_NAME`.
- Reports displays SMTP readiness without exposing credentials.
- Monthly/yearly reports are enabled by default.
- Reports are sent only to users:
  - active
  - with email notifications enabled
- Monthly and yearly templates can independently use ten styles, including Editorial, Dashboard, Receipt, Statement, Magazine, Minimal and Neon, with previews based on real report data and shared branding.

## License

This project is licensed under the [MIT License](./LICENSE).
