# Finance v3.8.0 - Operación, módulos opcionales e i18n modular

## Cambios principales

- `DATABASE_URL` es la única fuente de configuración de PostgreSQL; se elimina el fichero de configuración histórico y la gestión de BD desde la aplicación.
- SMTP se configura exclusivamente mediante variables de entorno. Informes conserva estado, pruebas e historial de entregas.
- Cuentas clasificadas (`current`, `savings`, `cash`, `other`), saldo inicial y agregado consolidado de cuentas de ahorro.
- Moneda global configurable para toda la interfaz, sin conversión de importes históricos.
- Backups internos programados, retención por días, verificación, descarga y restauración segura.
- Préstamos y Presupuestos son módulos opcionales administrados desde **Gestión → Módulos** con un único botón **Guardar**.
- Desactivar un módulo oculta su navegación y contenido relacionado, bloquea sus rutas y conserva íntegramente sus datos e histórico.
- Inicio de la estructura modular de i18n en `backend/locales/`, compatible con todas las claves y llamadas actuales.

## Actualización

Configura PostgreSQL mediante una única variable de entorno:

```yaml
environment:
  DATABASE_URL: postgresql://usuario:contraseña@servidor:5432/base_de_datos
```

Las migraciones se aplican al iniciar. Las migraciones `028_optional_loans_module.sql` y `029_optional_budgets_module.sql` habilitan ambos módulos inicialmente; pueden cambiarse desde **Gestión → Módulos** sin pérdida de datos.
