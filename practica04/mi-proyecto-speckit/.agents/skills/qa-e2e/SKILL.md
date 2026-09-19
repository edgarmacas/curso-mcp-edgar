---
name: qa-e2e
description: Audita los tests end-to-end existentes (proceso completo, vía subprocess) contra specs/*/spec.md y agrega solo lo que falta, sin improvisar el flujo ni duplicar lo ya cubierto.
---
# Instrucciones
1. Lee `specs/*/spec.md`, sección "Acceptance Scenarios" — identifica los escenarios que describen el uso real de punta a punta, como lo usaría la persona que opera el programa. Si no existe ningún `specs/*/spec.md`, DETENTE y pide que se corra Spec Kit primero.
2. Revisa `tests/e2e/` (créala si no existe). Además, revisa si `tests/integration/` tiene algún archivo que en realidad use `subprocess` para lanzar el programa completo — si lo encuentras, muévelo a `tests/e2e/` con `git mv` (no lo reescribas, solo reubícalo) y avisa que lo hiciste.
3. Para cada escenario que no esté cubierto, agrega un test e2e nuevo: invoca el programa completo como lo haría un usuario real (vía `subprocess`, verificando stdout y código de salida), nunca llamando a una función interna directamente.
4. Corre `uv run pytest tests/e2e/ -v` y reporta el resultado.
