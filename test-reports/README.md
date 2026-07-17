# Informes locales de pruebas

Cada ejecución de pytest genera:

- `finance-test-report-YYYYMMDD-HHMMSS.md`: informe histórico de esa ejecución.
- `latest.md`: copia del informe más reciente.

Los informes contienen el catálogo completo de combinaciones ruta-método y el resultado de las comprobaciones de contrato HTTP, autenticación y CSRF. Los ficheros generados están ignorados por Git; este README sí se mantiene versionado.
