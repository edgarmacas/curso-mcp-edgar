---
name: qa-unit
description: Audita los tests unitarios existentes contra specs/*/spec.md (Acceptance Scenarios, Edge Cases, Functional Requirements) y agrega solo lo que falta, sin improvisar qué probar ni duplicar lo ya cubierto.
---
# Instrucciones
1. Lee `specs/*/spec.md` — secciones "Acceptance Scenarios", "Edge Cases" y "Functional Requirements" (revisa también `## Clarifications` si existe: ahí suelen vivir los requisitos agregados después de la implementación original). Si no existe ningún `specs/*/spec.md`, DETENTE y pide que se corra Spec Kit primero — no inventes criterios propios.
2. Si existe `tests/unit/`, revisa los tests que ya hay ahí antes de escribir nada.
3. Para cada escenario, caso borde o FR que corresponda a una función aislada: si ya hay un test que lo cubre, repórtalo como "ya cubierto en `<archivo>`" y no lo dupliques. Si no está cubierto, agrégalo con un assert real — dentro del archivo de `tests/unit/` que corresponda por tema, o en uno nuevo si no encaja en ninguno.
4. No agregues tests para casos que no estén en la spec — si crees que falta algo importante, sugiérelo al final, no lo generes por tu cuenta.
5. Corre `uv run pytest tests/unit/ -v` y reporta cuántos pasaron, cuántos fallaron, y cuántos tests eran nuevos.
