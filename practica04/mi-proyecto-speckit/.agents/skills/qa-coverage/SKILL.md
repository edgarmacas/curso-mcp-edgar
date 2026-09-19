---
name: qa-coverage
description: Ejecuta y resume el reporte de cobertura de tests del proyecto, señalando líneas sin probar.
---
# Instrucciones
1. Corre `uv run pytest --cov=src --cov-report=term-missing` (ajusta `src` si tu código no vive bajo esa carpeta).
2. Resume: porcentaje total, y qué líneas "Missing" son casos borde olvidados vs. código no usado.
3. No agregues tests automáticamente — solo diagnostica.
