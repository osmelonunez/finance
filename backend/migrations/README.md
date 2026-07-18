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
- `003_notifications_schema.sql`: tablas de SMTP y reportes por email: `smtp_settings`, `email_report_config` y `email_report_runs`.
- `004_seed_defaults.sql`: valores iniciales de settings, backups, SMTP, reportes y categorias por defecto.
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
- `003_notifications_schema.sql`: SMTP and email reporting tables: `smtp_settings`, `email_report_config`, and `email_report_runs`.
- `004_seed_defaults.sql`: initial settings, backup, SMTP, report, and default category values.
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
