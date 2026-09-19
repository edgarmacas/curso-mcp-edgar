---
name: qa-orchestrate
description: Ejecuta el flujo completo de calidad invocando en orden a tester-agent, security-agent y report-agent, sin pedir confirmación entre cada uno.
---
# Instrucciones
1. Verifica que exista `specs/*/spec.md`. Si falta, detente y pide que se corra Spec Kit primero.
2. Invoca al agente tester-agent (su propia tarea vive en su `agent.md`). Espera a que termine por completo.
3. Invoca al agente security-agent (su propia tarea vive en su `agent.md`). Espera a que termine por completo.
4. Invoca al agente report-agent (su propia tarea vive en su `agent.md`).
5. Presenta al usuario el veredicto final, con un resumen de 1 línea de qué hizo cada agente en el camino.

No pidas confirmación entre fase y fase — este es un flujo automático de punta a punta. Si `agy` te pide aprobar el permiso de invocación de cada agente, apruébalo y sigue.
