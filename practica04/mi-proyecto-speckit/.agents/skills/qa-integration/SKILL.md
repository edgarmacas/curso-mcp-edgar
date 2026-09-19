---
name: qa-integration
description: Audita el test de integración EN MEMORIA (sin subprocess) existente contra specs/*/spec.md y agrega solo lo que falta, sin improvisar el flujo a probar ni duplicar lo ya cubierto.
---
# Instrucciones
1. Lee `specs/*/spec.md`, sección "Acceptance Scenarios" — identifica los escenarios que requieren que 2+ módulos de tu propio código se conecten (ej. tu CLI llamando a tu lógica de negocio). Si no existe ningún `specs/*/spec.md`, DETENTE y pide que se corra Spec Kit primero.
2. Si existe `tests/integration/`, revisa qué flujo ya prueba antes de escribir nada. Si algún archivo ahí usa `subprocess` para lanzar el programa completo, NO es integración — es un test e2e mal clasificado. No lo toques ni lo dupliques: repórtalo, la skill `qa-e2e` se encarga de reubicarlo.
3. Si el escenario ya está cubierto por un test real en memoria, repórtalo como "ya cubierto en `<archivo>`" y no lo dupliques.
4. Si falta, agrega un test **en memoria** (llama directamente a las funciones que conectan tus módulos, sin lanzar el programa como proceso aparte) en el archivo existente o en uno nuevo dentro de `tests/integration/`.
5. Corre `uv run pytest tests/integration/ -v` y reporta el resultado.
