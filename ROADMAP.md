# Roadmap (bloques evolutivos)

Este roadmap separa:
- hotfixes/bugfixes
- mejoras/optimizaciones planificadas
- funcionalidades nuevas a valorar (no comprometidas)

## Hardening + Operación
- Completado en `v3.1.0`.

## Rendimiento y Mantenibilidad
- Completado en `v3.1.0`.

## Robustez de Datos y UX Técnica
- Límites de longitud en campos de texto (backend + base de datos).
- Protección anti doble envío en acciones críticas.
- Revisión de paginación para grandes volúmenes (evaluar keyset).
- Uniformidad de logs por evento de negocio.

## Gestión Funcional
- Evolución de “Cuentas y tarjetas” con reglas más claras.
- Mejoras en asociación de gastos a cuenta/tarjeta.
- Plantillas de reportes `v2` y opciones de branding.
- Evolución de i18n (estructura más modular de traducciones).

## Escalabilidad Doméstica + Observabilidad
- Métricas operativas básicas (latencias por ruta, tasa de errores).
- Retención configurable de logs de negocio en base de datos.
- Mejora de rendimiento en listados masivos/exportaciones.
- Scripts y documentación operativa de mantenimiento.

## Funcionalidades a valorar (no comprometidas)
- Adjuntar facturas/recibos (PDF/imagen) a gastos.
- Notificaciones internas en la aplicación (alertas/recordatorios).
- Reglas automáticas por categoría/origen/cuenta.
- Presupuestos por categoría con alertas de desviación.
- Importador bancario CSV con mapeo de columnas.
- Cierre mensual guiado (checklist + snapshot).
- Exportación de reportes a PDF.
- Comparativas avanzadas por periodos (MoM/YoY).
- Soporte multi-moneda.
- API tokens para integraciones externas.
