# Finance v3.6.0 - Banca e integración de préstamos

Esta versión consolida bancos, cuentas y tarjetas en el espacio **Banca** e integra la información de los préstamos sin mezclar deuda, capital utilizado y saldo disponible.

## Cambios principales

- Las tarjetas pasan a depender de una cuenta mediante la migración `015_cards_linked_to_accounts.sql`.
- La vista Relaciones representa la jerarquía Banco → Cuenta → Tarjeta con conexiones directas.
- El detalle de banco muestra los préstamos asociados y KPI de capital prestado, deuda pendiente, importe amortizado y cuota mensual.
- Los bancos que solo tienen préstamos muestran un estado sin información de saldo, sin crear cuentas ficticias.
- Las gráficas bancarias contabilizan los pagos de préstamos, incluidos capital e intereses, pero no los usos del capital prestado.
- Se mantienen el formato monetario localizado, las traducciones en español e inglés y la navegación existente.
- Los datos demo de ING incluyen tres cuentas y cuatro tarjetas correctamente vinculadas.

## Compatibilidad y validación

- Las tarjetas existentes sin cuenta asignada se conservan para permitir una transición compatible.
- Se cubren rutas, permisos, cálculos, estados vacíos, relaciones, integridad y paginación mediante pruebas automáticas.

## Artefactos previstos

- Imagen: `f1nanc3/finance:3.6.0`
- Imagen flotante: `f1nanc3/finance:latest`
- Tag Git previsto: `v3.6.0`

No se han creado todavía el tag, la release ni la publicación de la imagen.
