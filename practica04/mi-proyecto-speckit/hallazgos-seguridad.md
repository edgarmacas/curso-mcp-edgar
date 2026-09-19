# Hallazgos de Seguridad

| Caso | Lo que se encontró | Corrección sugerida |
|---|---|---|
| 🔑 Secreto expuesto | sin hallazgos | Ninguna requerida. No se encontraron credenciales ni tokens quemados en el código. |
| 🧪 Validación de entradas | sin hallazgos | El código valida tipos numéricos, rangos físicos y cadenas de unidad válidas. |
| 🚪 Manejo de excepciones | sin hallazgos | Se implementan excepciones específicas de dominio (`TemperatureConversionError`, `AbsoluteZeroViolationError`). |

## Acciones de higiene aplicadas
- Se creó el archivo `.env.example` para documentar la configuración de variables de entorno.
- Se agregó la regla `.env` y `.env.*` al `.gitignore` para asegurar que ningún secreto sea rastreado accidentalmente por Git.
