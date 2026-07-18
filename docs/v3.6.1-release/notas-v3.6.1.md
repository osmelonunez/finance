# Finance v3.6.1 - Nombres de cuentas y tarjetas por contexto

Este hotfix corrige la restricción global que impedía utilizar nombres habituales como `Cuenta compartida` en bancos diferentes.

## Cambios

- Una cuenta solo debe tener un nombre único dentro de su banco.
- Los nombres de tarjeta pueden repetirse incluso dentro de una misma cuenta porque su identidad depende del `id`.
- Los nombres de cuenta se pueden reutilizar en bancos diferentes.
- Los formularios muestran mensajes específicos cuando el duplicado pertenece a la misma entidad padre.
- Las migraciones `016_payment_method_names_scoped_to_parent.sql` y `017_card_names_not_unique.sql` limitan la unicidad de cuentas a su banco y eliminan la unicidad de nombres de tarjeta sin modificar ni eliminar datos existentes.

## Validación prevista

- Migraciones sobre PostgreSQL aislado.
- Integridad de altas y ediciones.
- Rutas, permisos y regresión completa.

No se han creado todavía el commit, la PR, el tag, la release ni las imágenes de esta versión.
