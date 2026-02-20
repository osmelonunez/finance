# Roadmap (desde 3.0.0)

Este roadmap separa:
- mejoras/optimizaciones planificadas
- funcionalidades nuevas a valorar (no comprometidas)

## 3.0.1 (Hardening + Operación)
- Rotación de logs Docker (`max-size: 10m`, `max-file: 7`).
- Redacción de secretos en logs (password, token, URLs con credenciales).
- Ajustes de seguridad de sesión/cookies y cabeceras HTTP.
- Endpoints de salud (`/health/live`, `/health/ready`).
- Mensajes de error genéricos en UI + detalle técnico en logs.

## 3.1.0 (Rendimiento y Mantenibilidad)
- Índices compuestos en `records` según filtros reales.
- Optimización de queries de dashboard (menos roundtrips a BD).
- Caché corto de agregados de dashboard (15-60 segundos).
- Capa versionada de plantillas de reportes (base `v1`).
- Refactor de validaciones comunes (concepto, importe, fecha).

## 3.1.1 (Robustez de Datos y UX Técnica)
- Límites de longitud en campos de texto (backend + base de datos).
- Protección anti doble envío en acciones críticas.
- Revisión de paginación para grandes volúmenes (evaluar keyset).
- Uniformidad de logs por evento de negocio.

## 3.2.0 (Gestión Funcional)
- Evolución de “Cuentas y tarjetas” con reglas más claras.
- Mejoras en asociación de gastos a cuenta/tarjeta.
- Plantillas de reportes `v2` y opciones de branding.
- Evolución de i18n (estructura más modular de traducciones).

## 3.3.0 (Escalabilidad Doméstica + Observabilidad)
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
