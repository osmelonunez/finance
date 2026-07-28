# Database migrations

## Español

Las migraciones viven en esta carpeta como ficheros SQL planos. El runner de la app (`backend/migrations.py`) las aplica por orden alfabetico y guarda el nombre exacto del fichero en la tabla `migrations`.

### Como trabajar con migraciones

- Usa siempre un numero incremental de tres digitos: `007_descripcion.sql`.
- No edites una migracion que ya haya sido aplicada en una instancia. Crea una nueva migracion.
- El nombre del fichero es el identificador de la migracion, asi que renombrar un fichero aplicado requiere ajustar manualmente la tabla `migrations`.
- Mantén cada migracion enfocada en una intencion clara: schema, seed, backfill, indexes o fix.
- Separa `seed` y `backfill` del schema cuando modifiquen datos existentes.
- Usa `IF NOT EXISTS`, `ON CONFLICT DO NOTHING` o pasos defensivos cuando tenga sentido para facilitar despliegues repetibles.
- Si una constraint depende de datos existentes, primero normaliza/backfillea los datos y despues añade la constraint en otra migracion.

### Migraciones actuales

- `001_core_schema.sql`: tablas e indices base de la app: `users`, `settings`, `categories`, `payment_methods` y `records`.
- `002_management_schema.sql`: tablas de administracion operativa: `backup_config` y `backup_runs`.
- `003_notifications_schema.sql`: tablas de configuracion e historial de reportes por email: `email_report_config` y `email_report_runs`.
- `004_seed_defaults.sql`: valores iniciales de settings, backups, reportes y categorias por defecto.
- `005_records_indexes.sql`: indices compuestos para filtros y ordenacion habituales de `records`.
- `006_add_loans.sql`: esquema de prestamos y relacion con `records` para pagos de prestamos.
- `007_banks.sql`: catalogo de bancos y relacion con cuentas/tarjetas y prestamos.
- `008_drop_records_is_financed.sql`: elimina la marca obsoleta `is_financed` de `records`.
- `009_add_loan_usages.sql`: usos del capital de un prestamo sin impactar gastos mensuales ni ahorros.
- `010_loans_dashboard_visibility.sql`: permite excluir prestamos de los totales de prestamos del panel principal.
- `011_mortgage_loan_details.sql`: marca prestamos como hipoteca y separa amortizacion/intereses en pagos.
- `012_loan_interest_rate_text.sql`: permite guardar el interes de hipoteca como texto descriptivo.
- `013_loan_type_and_repayment.sql`: agrega tipo de prestamo y total previsto a devolver.
- `014_data_robustness_constraints.sql`: agrega limites de longitud defensivos para textos principales: conceptos y nombres a 40 caracteres, comentarios y descripciones a 500.
- `015_cards_linked_to_accounts.sql`: vincula cada tarjeta con su cuenta mediante `parent_account_id`, conservando de forma compatible las tarjetas existentes sin cuenta asignada.
- `016_payment_method_names_scoped_to_parent.sql`: sustituye la unicidad global por nombres de cuenta unicos dentro de cada banco y, como paso compatible, nombres de tarjeta unicos dentro de cada cuenta.
- `017_card_names_not_unique.sql`: elimina la restriccion temporal de unicidad de nombres de tarjeta por cuenta; las tarjetas se identifican exclusivamente por `id`.
- `018_category_budgets.sql`: crea el historico mensual de presupuestos por categoria, con importe positivo y una unica configuracion por categoria y mes.
- `019_budget_disabled_state.sql`: permite retirar un presupuesto vigente mediante un estado desactivado, conservando el historico y la herencia temporal.
- `020_saved_reports.sql`: guarda configuraciones reutilizables de Informes por usuario, incluyendo seccion y parametros de consulta.
- `021_savings_accounts.sql`: clasifica cuentas como corrientes o de ahorro, añade saldo inicial y permite asignar aportaciones de ahorro a una cuenta.
- `022_email_report_branding.sql`: añade la identidad Finance definitiva para las plantillas por email, con nombre, cabecera y pie alineado con el sitio.
- `023_remove_record_source.sql`: elimina el origen mensual/ahorro obsoleto de `records`; la cuenta asociada pasa a ser la única referencia financiera.
- `024_drop_smtp_settings.sql`: elimina la configuración SMTP persistida; SMTP pasa a depender exclusivamente del entorno.
- `025_backup_reliability.sql`: añade metadatos de verificación y auditoría a las copias de seguridad.
- `026_simplify_backup_retention.sql`: simplifica la retención automática de backups a días.
- `027_global_currency.sql`: añade la moneda global de la aplicación.
- `028_optional_loans_module.sql`: habilita por defecto el módulo opcional de préstamos.
- `029_optional_budgets_module.sql`: habilita por defecto el módulo opcional de presupuestos.

### Migraciones de v3.8.0

1. `024_drop_smtp_settings.sql`
   - Elimina `smtp_settings`.
   - No afecta `email_report_config` ni `email_report_runs`.
   - Antes de aplicarla, traslada las credenciales SMTP a variables de entorno.
2. `025_backup_reliability.sql`
   - Añade la verificación y el historial operativo de backups.
3. `026_simplify_backup_retention.sql`
   - Conserva la política de retención únicamente en días.
4. `027_global_currency.sql`
   - Guarda la moneda global que utiliza toda la interfaz.
5. `028_optional_loans_module.sql`
   - Activa inicialmente el módulo de préstamos.
   - Puede cambiarse desde Gestión → Módulos sin eliminar préstamos ni pagos históricos.
6. `029_optional_budgets_module.sql`
   - Activa inicialmente el módulo de presupuestos.
   - Puede cambiarse desde Gestión → Módulos sin eliminar presupuestos ni su histórico mensual.

### Migraciones de v3.7.0

Deben aplicarse en este orden:

1. `018_category_budgets.sql`
   - Crea `category_budgets`.
   - Relaciona cada presupuesto con `categories` mediante `category_id` y `ON DELETE RESTRICT`.
   - Guarda el mes como `YYYY-MM`, exige un importe positivo y evita duplicados con `UNIQUE (category_id, month)`.
   - Añade un indice por mes para resolver el presupuesto vigente y las consultas historicas.
2. `019_budget_disabled_state.sql`
   - Añade `is_disabled` y permite que `amount` sea nulo solo cuando el presupuesto esta desactivado.
   - Mantiene activas y sin cambios las filas creadas por la migracion anterior.
   - El estado desactivado actua como corte de vigencia: permite quitar el presupuesto actual o futuro sin borrar el historial de meses anteriores.
3. `020_saved_reports.sql`
   - Crea `saved_reports`, vinculada a `users` con `ON DELETE CASCADE`.
   - Conserva el nombre, la seccion de Informes y la cadena de parametros que reconstruye periodos, comparacion y filtros.
   - Añade un indice por usuario y fecha de creacion para listar sus configuraciones mas recientes.
4. `021_savings_accounts.sql`
   - Añade `account_type` e `initial_balance` a las cuentas.
   - Clasifica las cuentas bancarias como `current` o `savings`; las tarjetas heredan la clasificación de su cuenta padre.
   - Permite vincular `payment_method_id` tanto a gastos como a aportaciones `saving`.
5. `022_email_report_branding.sql`
   - Añade el branding compartido de las plantillas por email.
   - Configura el nombre, la cabecera y el pie predeterminados del sitio.
6. `023_remove_record_source.sql`
   - Elimina la columna obsoleta `records.source` y su índice compuesto.
   - Crea un índice por tipo y fecha para conservar el rendimiento de los listados.
   - Los gastos y ahorros quedan vinculados exclusivamente mediante `payment_method_id`.

Las comparativas, la evolucion financiera, los filtros y las exportaciones no necesitan tablas adicionales: consultan las relaciones ya existentes entre movimientos, categorias, bancos, cuentas, tarjetas y prestamos. La migracion `020` solo persiste la configuracion reutilizable, no una copia de los resultados financieros.

En instalaciones existentes, `018` y `020` empiezan sin datos; no generan presupuestos ni informes guardados automaticamente. Los datos de demostracion se insertan por el flujo de seed de la aplicacion, no mediante estas migraciones. No edites ni renombres una migracion despues de desplegarla: cualquier ajuste posterior debe añadirse como una nueva migracion.

Antes de aplicar `023_remove_record_source.sql` en una instalación existente:

1. Crea una copia de seguridad de PostgreSQL.
2. Comprueba que cada aportación de ahorro tiene una cuenta de ahorro asociada:

```sql
SELECT COUNT(*) AS savings_without_account
FROM records
WHERE type = 'saving'
  AND payment_method_id IS NULL;
```

3. Comprueba que los antiguos gastos con origen ahorro tienen una cuenta asociada:

```sql
SELECT COUNT(*) AS savings_expenses_without_account
FROM records
WHERE type = 'expense'
  AND source = 'saving'
  AND payment_method_id IS NULL;
```

Ambas consultas deben devolver `0`. Si no es así, asigna primero la cuenta correcta mediante `payment_method_id`. La segunda consulta solo puede ejecutarse antes de aplicar `023`, ya que esa migración elimina `records.source`.

Comprobacion rapida tras actualizar:

```sql
SELECT id
FROM migrations
WHERE id IN (
    '018_category_budgets.sql',
    '019_budget_disabled_state.sql',
    '020_saved_reports.sql',
    '021_savings_accounts.sql',
    '022_email_report_branding.sql',
    '023_remove_record_source.sql'
)
ORDER BY id;

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('category_budgets', 'saved_reports')
ORDER BY table_name;

SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'email_report_config'
  AND column_name IN ('brand_name', 'header_text', 'footer_text')
ORDER BY column_name;

SELECT COUNT(*) AS source_columns
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'records'
  AND column_name = 'source';
```

## English

Migrations live in this folder as plain SQL files. The app runner (`backend/migrations.py`) applies them in alphabetical order and stores the exact file name in the `migrations` table.

### How to work with migrations

- Always use an incremental three-digit number: `007_description.sql`.
- Do not edit a migration that has already been applied to an instance. Create a new migration instead.
- The file name is the migration identifier, so renaming an applied file requires a manual update in the `migrations` table.
- Keep each migration focused on one clear intention: schema, seed, backfill, indexes, or fix.
- Split `seed` and `backfill` from schema migrations when they modify existing data.
- Use `IF NOT EXISTS`, `ON CONFLICT DO NOTHING`, or defensive steps when they help make deployments repeatable.
- If a constraint depends on existing data, normalize/backfill the data first and add the constraint in a later migration.

### Current migrations

- `001_core_schema.sql`: core app tables and indexes: `users`, `settings`, `categories`, `payment_methods`, and `records`.
- `002_management_schema.sql`: operational management tables: `backup_config` and `backup_runs`.
- `003_notifications_schema.sql`: email report configuration and history tables: `email_report_config` and `email_report_runs`.
- `004_seed_defaults.sql`: initial settings, backup, report, and default category values.
- `005_records_indexes.sql`: compound indexes for common `records` filtering and sorting patterns.
- `006_add_loans.sql`: loans schema and the relationship with `records` for loan payments.
- `007_banks.sql`: bank catalog and relationship with accounts/cards and loans.
- `008_drop_records_is_financed.sql`: removes the obsolete `is_financed` flag from `records`.
- `009_add_loan_usages.sql`: loan capital usage tracking without affecting monthly expenses or savings.
- `010_loans_dashboard_visibility.sql`: allows loans to be excluded from dashboard loan totals.
- `011_mortgage_loan_details.sql`: marks loans as mortgages and splits principal/interest in payments.
- `012_loan_interest_rate_text.sql`: allows mortgage interest to be stored as descriptive text.
- `013_loan_type_and_repayment.sql`: adds loan type and expected total repayment.
- `014_data_robustness_constraints.sql`: adds defensive length limits for primary text fields: concepts and names to 40 characters, comments and descriptions to 500.
- `015_cards_linked_to_accounts.sql`: links each card to its account through `parent_account_id`, while compatibly preserving existing cards that do not yet have an assigned account.
- `016_payment_method_names_scoped_to_parent.sql`: replaces global uniqueness with account names unique within each bank and, as a compatible intermediate step, card names unique within each account.
- `017_card_names_not_unique.sql`: removes the temporary per-account card-name uniqueness rule; cards are identified exclusively by `id`.
- `018_category_budgets.sql`: creates monthly category budget history, with positive amounts and one configuration per category and month.
- `019_budget_disabled_state.sql`: allows an effective budget to be removed through a disabled state while preserving history and time-based inheritance.
- `020_saved_reports.sql`: stores reusable per-user Reports configurations, including the report section and query parameters.
- `021_savings_accounts.sql`: classifies accounts as current or savings, adds an initial balance, and allows saving contributions to target an account.
- `022_email_report_branding.sql`: adds the final Finance identity for email templates, with name, header, and site-aligned footer.
- `023_remove_record_source.sql`: removes the obsolete monthly/savings origin from `records`; the linked account becomes the sole financial reference.
- `024_drop_smtp_settings.sql`: removes persisted SMTP configuration; SMTP now depends exclusively on the environment.
- `025_backup_reliability.sql`: adds day-based backup retention and integrity checks for custom PostgreSQL dumps.
- `026_simplify_backup_retention.sql`: removes the temporary weekly/monthly retention fields from early v3.8.0 development databases.
- `027_global_currency.sql`: adds the global display currency setting, defaulting to EUR.
- `028_optional_loans_module.sql`: adds the global switch that hides and blocks the loans module without deleting data.
- `029_optional_budgets_module.sql`: adds the global switch that hides and blocks the budgets module without deleting data.

### v3.8.0 migrations

1. `024_drop_smtp_settings.sql`
   - Drops `smtp_settings`.
   - Does not affect `email_report_config` or `email_report_runs`.
   - Move SMTP credentials to environment variables before applying it.
2. `025_backup_reliability.sql`
   - Replaces the single retention count with one day-based retention window.
   - Adds SHA-256 verification metadata to backup runs.
   - Existing backup files remain on disk; create a fresh verified `.dump` before relying on restore.
3. `026_simplify_backup_retention.sql`
   - Removes temporary weekly/monthly retention fields created by an early v3.8.0 development build.
4. `027_global_currency.sql`
   - Adds a single global display currency (`EUR` by default).
   - It changes formatting only; amounts are not converted.
5. `028_optional_loans_module.sql`
   - Adds the `loans_enabled` global setting, enabled by default.
   - Disabling it preserves loans and history while hiding the module and blocking its routes.
6. `029_optional_budgets_module.sql`
   - Adds the `budgets_enabled` global setting, enabled by default.
   - Disabling it preserves budget configuration and monthly history while hiding the module and blocking its routes.

### v3.7.0 migrations

They must be applied in this order:

1. `018_category_budgets.sql`
   - Creates `category_budgets`.
   - Links each budget to `categories` through `category_id` with `ON DELETE RESTRICT`.
   - Stores months as `YYYY-MM`, requires a positive amount, and prevents duplicates with `UNIQUE (category_id, month)`.
   - Adds a month index for effective-budget resolution and historical queries.
2. `019_budget_disabled_state.sql`
   - Adds `is_disabled` and allows `amount` to be null only when the budget is disabled.
   - Leaves rows created by the previous migration active and unchanged.
   - The disabled state acts as an effective-date boundary: it removes the current or future budget without deleting previous-month history.
3. `020_saved_reports.sql`
   - Creates `saved_reports`, linked to `users` with `ON DELETE CASCADE`.
   - Stores the name, Reports section, and query string used to reconstruct periods, comparison settings, and filters.
   - Adds a user and creation-date index for listing the newest configurations.
4. `021_savings_accounts.sql`
   - Adds `account_type` and `initial_balance` to accounts.
   - Classifies bank accounts as `current` or `savings`; cards inherit their parent account classification.
   - Allows `payment_method_id` on both expenses and `saving` contributions.
5. `022_email_report_branding.sql`
   - Adds shared branding for email report templates.
   - Configures the default site name, header, and footer.
6. `023_remove_record_source.sql`
   - Removes the obsolete `records.source` column and its compound index.
   - Creates a type-and-date index to retain list-query performance.
   - Expenses and savings are linked exclusively through `payment_method_id`.

Comparisons, financial evolution, filters, and exports require no additional tables: they query the existing relationships between records, categories, banks, accounts, cards, and loans. Migration `020` persists only the reusable configuration, not a copy of the financial results.

On existing installations, `018` and `020` start empty; they do not create budgets or saved reports automatically. Demo data is inserted through the application's seed flow, not through these migrations. Do not edit or rename a migration after deployment; add a new migration for any later adjustment.

Before applying `023_remove_record_source.sql` to an existing installation:

1. Create a PostgreSQL backup.
2. Confirm that every saving contribution has an assigned savings account:

```sql
SELECT COUNT(*) AS savings_without_account
FROM records
WHERE type = 'saving'
  AND payment_method_id IS NULL;
```

3. Confirm that legacy savings-funded expenses have an assigned account:

```sql
SELECT COUNT(*) AS savings_expenses_without_account
FROM records
WHERE type = 'expense'
  AND source = 'saving'
  AND payment_method_id IS NULL;
```

Both queries must return `0`. Otherwise, assign the correct account through `payment_method_id` first. The second query can only run before `023`, because that migration removes `records.source`.

Quick verification after upgrading:

```sql
SELECT id
FROM migrations
WHERE id IN (
    '018_category_budgets.sql',
    '019_budget_disabled_state.sql',
    '020_saved_reports.sql',
    '021_savings_accounts.sql',
    '022_email_report_branding.sql',
    '023_remove_record_source.sql'
)
ORDER BY id;

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('category_budgets', 'saved_reports')
ORDER BY table_name;

SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'email_report_config'
  AND column_name IN ('brand_name', 'header_text', 'footer_text')
ORDER BY column_name;

SELECT COUNT(*) AS source_columns
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'records'
  AND column_name = 'source';
```
