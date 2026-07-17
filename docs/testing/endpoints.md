# Catálogo de endpoints y cobertura automática

Este fichero se genera desde el registro de rutas de Flask. No debe editarse manualmente.

- Reglas de aplicación: **86**.
- Combinaciones endpoint-método: **92**.
- Se excluyen la ruta estática y los métodos automáticos `HEAD` y `OPTIONS`.
- `Contrato`, `Autenticación` y `CSRF` indican que existe una comprobación automática genérica.
- `Prueba específica` identifica cobertura funcional adicional; `—` significa que solo tiene cobertura genérica.

| Ruta | Método | Endpoint | Acceso | Contrato | Autenticación | CSRF | Prueba específica |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/` | GET | `dashboard.dashboard` | Autenticado | Sí | Sí | N/A | — |
| `/categories` | GET | `categories.categories` | Autenticado | Sí | Sí | N/A | — |
| `/categories/<int:category_id>/delete` | POST | `categories.delete_category` | Autenticado | Sí | Sí | Sí | `test_category_create_update_delete_flow` |
| `/categories/<int:category_id>/update` | POST | `categories.update_category` | Autenticado | Sí | Sí | Sí | `test_category_create_update_delete_flow` |
| `/categories/add` | POST | `categories.add_category` | Autenticado | Sí | Sí | Sí | `test_category_create_update_delete_flow` |
| `/delete-all` | POST | `movements.delete_all` | Autenticado | Sí | Sí | Sí | — |
| `/delete/<int:id>` | POST | `movements.delete` | Autenticado | Sí | Sí | Sí | `test_expense_create_edit_duplicate_delete_flow` |
| `/duplicate/<int:id>` | GET | `movements.duplicate` | Autenticado | Sí | Sí | N/A | `test_expense_create_edit_duplicate_delete_flow` |
| `/duplicate/<int:id>` | POST | `movements.duplicate` | Autenticado | Sí | Sí | Sí | `test_expense_create_edit_duplicate_delete_flow` |
| `/edit/<int:id>` | GET | `movements.edit` | Autenticado | Sí | Sí | N/A | `test_expense_create_edit_duplicate_delete_flow` |
| `/edit/<int:id>` | POST | `movements.edit` | Autenticado | Sí | Sí | Sí | `test_expense_create_edit_duplicate_delete_flow` |
| `/health/live` | GET | `health_live` | Público | Sí | N/A | N/A | — |
| `/health/ready` | GET | `health_ready` | Público | Sí | N/A | N/A | — |
| `/loans` | GET | `loans.loans_list` | Autenticado | Sí | Sí | N/A | — |
| `/loans/<int:id>` | GET | `loans.loan_detail` | Autenticado | Sí | Sí | N/A | — |
| `/loans/<int:id>/dashboard-visibility` | POST | `loans.loan_dashboard_visibility` | Autenticado | Sí | Sí | Sí | — |
| `/loans/<int:id>/delete` | POST | `loans.loan_delete` | Autenticado | Sí | Sí | Sí | — |
| `/loans/<int:id>/details` | POST | `loans.loan_details_update` | Autenticado | Sí | Sí | Sí | — |
| `/loans/<int:id>/status` | POST | `loans.loan_status` | Autenticado | Sí | Sí | Sí | — |
| `/loans/<int:id>/usages/<int:usage_id>/delete` | POST | `loans.loan_usage_delete` | Autenticado | Sí | Sí | Sí | `test_loan_usage_create_update_delete_flow` |
| `/loans/<int:id>/usages/<int:usage_id>/update` | POST | `loans.loan_usage_update` | Autenticado | Sí | Sí | Sí | `test_loan_usage_create_update_delete_flow` |
| `/loans/<int:id>/usages/add` | POST | `loans.loan_usage_add` | Autenticado | Sí | Sí | Sí | `test_loan_usage_create_update_delete_flow` |
| `/loans/add` | GET | `loans.loan_add` | Autenticado | Sí | Sí | N/A | — |
| `/loans/add` | POST | `loans.loan_add` | Autenticado | Sí | Sí | Sí | — |
| `/login` | GET | `auth.login` | Público | Sí | N/A | N/A | — |
| `/login` | POST | `auth.login` | Público | Sí | N/A | Sí | — |
| `/logout` | GET | `auth.logout` | Autenticado | Sí | Sí | N/A | — |
| `/management` | GET | `management.management` | Autenticado | Sí | Sí | N/A | `test_role_access_matrix` |
| `/management/backups` | GET | `backups.backups_page` | Autenticado | Sí | Sí | N/A | `test_role_access_matrix` |
| `/management/backups/config` | POST | `backups.backups_update_config` | Autenticado | Sí | Sí | Sí | — |
| `/management/backups/delete/<int:run_id>` | POST | `backups.backups_delete_run_file` | Autenticado | Sí | Sí | Sí | — |
| `/management/backups/download-latest` | GET | `backups.backups_download_latest` | Autenticado | Sí | Sí | N/A | — |
| `/management/backups/download/<int:run_id>` | GET | `backups.backups_download_run` | Autenticado | Sí | Sí | N/A | — |
| `/management/backups/restore/<int:run_id>` | POST | `backups.backups_restore_run` | Autenticado | Sí | Sí | Sí | — |
| `/management/backups/run-now` | POST | `backups.backups_run_now` | Autenticado | Sí | Sí | Sí | — |
| `/management/banks/<int:bank_id>/delete` | POST | `management.delete_bank` | Autenticado | Sí | Sí | Sí | `test_bank_with_linked_methods_cannot_be_deleted` |
| `/management/banks/<int:bank_id>/update` | POST | `management.update_bank` | Autenticado | Sí | Sí | Sí | `test_deactivating_bank_deactivates_linked_methods` |
| `/management/banks/add` | POST | `management.add_bank` | Autenticado | Sí | Sí | Sí | — |
| `/management/categories` | GET | `categories.management_categories` | Autenticado | Sí | Sí | N/A | — |
| `/management/database` | GET | `management.management_database` | Autenticado | Sí | Sí | N/A | — |
| `/management/db-connection/rollback` | POST | `management.rollback_db_connection` | Autenticado | Sí | Sí | Sí | — |
| `/management/db-connection/save` | POST | `management.save_db_connection` | Autenticado | Sí | Sí | Sí | — |
| `/management/db-connection/test` | POST | `management.test_db_connection` | Autenticado | Sí | Sí | Sí | — |
| `/management/demo-data/clear` | POST | `management.clear_demo_data` | Autenticado | Sí | Sí | Sí | — |
| `/management/demo-data/seed` | POST | `management.seed_demo_data` | Autenticado | Sí | Sí | Sí | — |
| `/management/email-reports/save` | POST | `management.save_email_reports` | Autenticado | Sí | Sí | Sí | — |
| `/management/email-reports/test-monthly` | POST | `management.test_monthly_report` | Autenticado | Sí | Sí | Sí | — |
| `/management/email-reports/test-yearly` | POST | `management.test_yearly_report` | Autenticado | Sí | Sí | Sí | — |
| `/management/initial-saving` | POST | `management.update_initial_saving` | Autenticado | Sí | Sí | Sí | — |
| `/management/payment-methods` | GET | `management.legacy_management_payment_methods` | Autenticado | Sí | Sí | N/A | — |
| `/management/payment-methods/<int:method_id>` | GET | `management.legacy_payment_method_detail` | Autenticado | Sí | Sí | N/A | — |
| `/management/payment-methods/<int:method_id>/delete` | POST | `management.delete_payment_method` | Autenticado | Sí | Sí | Sí | `test_payment_method_with_movements_cannot_be_deleted` |
| `/management/payment-methods/<int:method_id>/update` | POST | `management.update_payment_method` | Autenticado | Sí | Sí | Sí | — |
| `/management/payment-methods/add` | POST | `management.add_payment_method` | Autenticado | Sí | Sí | Sí | `test_valid_card_is_created` |
| `/management/records-years` | POST | `management.update_records_years` | Autenticado | Sí | Sí | Sí | — |
| `/management/reset-db` | POST | `management.reset_db` | Autenticado | Sí | Sí | Sí | — |
| `/management/smtp` | GET | `management.management_smtp` | Autenticado | Sí | Sí | N/A | — |
| `/management/smtp/save` | POST | `management.save_smtp` | Autenticado | Sí | Sí | Sí | — |
| `/management/smtp/test` | POST | `management.test_smtp` | Autenticado | Sí | Sí | Sí | — |
| `/management/system` | GET | `management.management_system` | Autenticado | Sí | Sí | N/A | — |
| `/management/users` | GET | `management.management_users` | Autenticado | Sí | Sí | N/A | `test_role_access_matrix` |
| `/management/users/<int:user_id>/role` | POST | `management.update_role` | Autenticado | Sí | Sí | Sí | — |
| `/management/users/<int:user_id>/toggle` | POST | `management.toggle_user` | Autenticado | Sí | Sí | Sí | — |
| `/payment-methods` | GET | `management.management_payment_methods` | Autenticado | Sí | Sí | N/A | `test_role_access_matrix` |
| `/payment-methods/<int:method_id>` | GET | `management.payment_method_detail` | Autenticado | Sí | Sí | N/A | — |
| `/payment-methods/<int:method_id>/delete` | POST | `management.delete_payment_method` | Autenticado | Sí | Sí | Sí | `test_payment_method_with_movements_cannot_be_deleted` |
| `/payment-methods/<int:method_id>/update` | POST | `management.update_payment_method` | Autenticado | Sí | Sí | Sí | — |
| `/payment-methods/<section>` | GET | `management.payment_methods_section` | Autenticado | Sí | Sí | N/A | `test_role_access_matrix` |
| `/payment-methods/add` | POST | `management.add_payment_method` | Autenticado | Sí | Sí | Sí | `test_valid_card_is_created` |
| `/payment-methods/banks/<int:bank_id>` | GET | `management.bank_detail` | Autenticado | Sí | Sí | N/A | `test_bank_detail_pagination_loads_second_page` |
| `/payment-methods/banks/<int:bank_id>/delete` | POST | `management.delete_bank` | Autenticado | Sí | Sí | Sí | `test_bank_with_linked_methods_cannot_be_deleted` |
| `/payment-methods/banks/<int:bank_id>/update` | POST | `management.update_bank` | Autenticado | Sí | Sí | Sí | `test_deactivating_bank_deactivates_linked_methods` |
| `/payment-methods/banks/add` | POST | `management.add_bank` | Autenticado | Sí | Sí | Sí | — |
| `/profile` | GET | `auth.profile` | Autenticado | Sí | Sí | N/A | — |
| `/profile/email` | POST | `auth.update_email` | Autenticado | Sí | Sí | Sí | — |
| `/profile/email-notifications` | POST | `auth.update_email_notifications_pref` | Autenticado | Sí | Sí | Sí | — |
| `/profile/language` | POST | `auth.update_language_pref` | Autenticado | Sí | Sí | Sí | — |
| `/profile/password` | POST | `auth.update_password` | Autenticado | Sí | Sí | Sí | — |
| `/profile/per-page` | POST | `auth.update_per_page_pref` | Autenticado | Sí | Sí | Sí | — |
| `/profile/username` | POST | `auth.update_username` | Autenticado | Sí | Sí | Sí | — |
| `/records/<int:id>` | GET | `movements.movement_detail` | Autenticado | Sí | Sí | N/A | — |
| `/records/add` | GET | `movements.add_movement` | Autenticado | Sí | Sí | N/A | `test_expense_create_edit_duplicate_delete_flow` |
| `/records/add` | POST | `movements.add_movement` | Autenticado | Sí | Sí | Sí | `test_expense_create_edit_duplicate_delete_flow` |
| `/records/expense` | GET | `movements.records_expense` | Autenticado | Sí | Sí | N/A | — |
| `/records/income` | GET | `movements.records_income` | Autenticado | Sí | Sí | N/A | — |
| `/records/saving` | GET | `movements.records_saving` | Autenticado | Sí | Sí | N/A | — |
| `/register` | GET | `auth.register` | Público | Sí | N/A | N/A | — |
| `/register` | POST | `auth.register` | Público | Sí | N/A | Sí | — |
| `/setup` | GET | `setup.setup_page` | Público | Sí | N/A | N/A | — |
| `/setup/create-new` | POST | `setup.setup_create_new` | Público | Sí | N/A | Sí | — |
| `/setup/test-connection` | POST | `setup.setup_test_connection` | Público | Sí | N/A | Sí | — |
| `/setup/use-existing` | POST | `setup.setup_use_existing` | Público | Sí | N/A | Sí | — |
