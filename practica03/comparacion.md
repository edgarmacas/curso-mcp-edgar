# Comparación de Enfoques: Spec a Mano vs. Spec Kit

**Sesión 4 · Programación de Backend y MCP en Python para IA Generativa**  
**Proyecto**: Convertidor de Temperatura (Celsius, Fahrenheit, Kelvin)

---

## 1. Tabla Comparativa de los 3 Casos de Prueba

| Caso | Entrada / Escenario | Resultado Spec a mano (3.A) | Resultado Spec Kit (3.B) |
|---|---|---|---|
| **Caso normal** | `convert_temperature(100, "C", "F")` | `212.0` | `212.00` |
| **Caso borde de la spec** | `convert_temperature(-5, "K", "C")` | `ValueError: Error de límite físico: La temperatura en Kelvin no puede ser menor a 0 K. Recibido: -5.0 K.` | `AbsoluteZeroViolationError: La temperatura -5.00 K está por debajo del cero absoluto (mínimo permitido: 0.00 K).` |
| **Caso no contemplado** | `convert_temperature(" 98.6 ", "°f", "kelvin")` | `310.15` | `310.15` (normalización tolerante de espacios, símbolos `°` y strings de unidad) |

---

## 2. Comparación de Metodologías

| Aspecto | Spec a mano | Spec Kit |
|---|---|---|
| **¿Cubrió los mismos casos borde?** | Sí, cubrió los casos borde explícitamente escritos (no numérico, identidad, cero absoluto, negativos). | Sí, y expandió sistemáticamente a límites físicos exactos (-273.15 °C, -459.67 °F, 0 K) y entradas NaN/Infinito. |
| **¿Qué generó Spec Kit que tú no habías escrito?** | Una especificación concisa de 14 líneas con un script directo y tests básicos. | Un árbol completo de diseño con contratos (`cli-contract.md`, `python-api.md`), modelo de datos formal, guía de quickstart, 20 tareas atómicas y 44 pruebas unitarias y de integración automáticas. |
| **¿Qué se sintió más rápido de arrancar?** | Spec a mano (un único archivo markdown y una instrucción directa al agente). | Spec a mano es más rápido para arrancar de inmediato en tareas muy pequeñas, mientras que Spec Kit requiere seguir los pasos de init, specify, plan y tasks. |
| **¿Cuál te generó más confianza en el resultado?** | Confiable para un script pequeño, pero con riesgo de lagunas si el problema escala. | Spec Kit generó sustancialmente mayor confianza debido al desglose de requisitos por historias de usuario, validación de checklists, contratos formales y cobertura exhaustiva de pruebas (44 tests pasando en 0.29s). |

---

## 3. Frase de Cierre

> "La próxima vez que tenga un proyecto de tamaño **mediano o grande**, elegiría **Spec Kit** porque proporciona una arquitectura desacoplada, contratos de interfaz claros, verificación rigurosa mediante checklists y una cobertura de pruebas automatizadas que previene regresiones y errores imprevistos."
