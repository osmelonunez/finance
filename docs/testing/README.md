# Documentación de pruebas

- `endpoints.md`: catálogo generado automáticamente desde las rutas registradas en Flask.
- Cada ejecución de pytest actualiza el catálogo para evitar que quede desfasado.
- `make test-endpoints` permite regenerarlo sin ejecutar la suite completa.

Los informes de cada ejecución se guardan fuera de la documentación versionada, en `test-reports/`.
