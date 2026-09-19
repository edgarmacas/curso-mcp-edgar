# Resultados de Pruebas — Bloque 3.B (Spec Kit)

Proyecto: **Convertidor de Temperatura (Celsius, Fahrenheit, Kelvin)**  
Especificación y flujo: Spec Kit (`/speckit-specify` $\rightarrow$ `/speckit-plan` $\rightarrow$ `/speckit-tasks` $\rightarrow$ `/speckit-implement`)

---

## Comparativa de los 3 Casos de Prueba (Bloque 3.A vs Bloque 3.B)

| Caso | Entrada / Escenario | Resultado Spec a Mano (3.A) | Resultado Spec Kit (3.B) | Estado |
|---|---|---|---|:---:|
| **Caso normal** | `convert_temperature(100, "C", "F")` | `212.0` | `212.00` | ✅ PASÓ |
| **Caso borde de la spec** | `convert_temperature(-5, "K", "C")` | Error: `ValueError: ... menor a 0 K` | Error de dominio: `AbsoluteZeroViolationError: La temperatura -5.00 K está por debajo del cero absoluto (mínimo permitido: 0.00 K).` | ✅ PASÓ |
| **Caso no contemplado** | `convert_temperature(" 98.6 ", "°f", "kelvin")` | `310.15` | `310.15` (normalización de espacios, símbolos `°` y nombres textuales de escala) | ✅ PASÓ |

---

## Métricas de Implementación Generada por Spec Kit

- **Total de tareas ejecutadas en `tasks.md`**: 20 / 20 (100% completadas).
- **Pruebas automatizadas generadas**: 44 tests (unitarios y de integración).
- **Tiempo de ejecución de la suite (`pytest`)**: 0.29 segundos (100% aprobadas).
- **Puntos de entrada implementados**:
  - Biblioteca Python: `from temperature_converter import convert_temperature, Scale`
  - Ejecutable CLI: `python -m temperature_converter <valor> <origen> <destino>` y script `convert-temp`
