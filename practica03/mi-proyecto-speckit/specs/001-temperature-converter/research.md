# Research & Technical Decisions: Convertidor de Temperatura

**Feature**: `001-temperature-converter`
**Status**: Completed

## Context & Objectives

El objetivo es implementar un convertidor de temperatura bidireccional entre Celsius (°C), Fahrenheit (°F) y Kelvin (K), que cumpla con los requisitos funcionales de validación del cero absoluto, redondeo a 2 decimales y manejo robusto de errores sin excepciones no controladas.

---

## Technical Decisions

### 1. Arquitectura del Proyecto y Empaquetado

- **Decision**: Estructurar el proyecto como un paquete Python estándar en `src/temperature_converter/` con soporte dual: como biblioteca importable y como interfaz de línea de comandos (CLI), administrado mediante `pyproject.toml` y `uv`.
- **Rationale**: Cumple con el principio de diseño "Library-First" y "CLI Interface", permitiendo tanto reutilización programática como ejecución directa desde la terminal sin dependencias externas pesadas.
- **Alternatives considered**:
  - *Script monolítico plano (`converter.py` en la raíz)*: Más simple para scripts pequeños, pero dificulta la distribución, empaquetado y pruebas modulares estructuradas.
  - *Framework web (FastAPI/Flask)*: Excesivo para un requerimiento de cálculo matemático local; añade complejidad innecesaria (YAGNI).

### 2. Aritmética, Precisión y Redondeo

- **Decision**: Utilizar tipos numéricos `float` para el cálculo interno de las conversiones termodinámicas y redondear el resultado final a 2 decimales mediante `round(valor, 2)`.
- **Rationale**: Las escalas termométricas estándar utilizan relaciones de primer grado con factores fraccionarios exactos (ej. 9/5 y 5/9, constante 273.15). `float` en Python 3.12 ofrece precisión IEEE 754 de doble precisión (64 bits), más que suficiente para garantizar exactitud a 2 decimales con latencia sub-microsegundo.
- **Alternatives considered**:
  - *Módulo `decimal.Decimal`*: Ofrece precisión decimal arbitraria, pero agrega sobrecarga de conversión de tipos innecesaria para un conversor de temperatura donde la precisión física requerida es de 2 decimales.

### 3. Fórmulas Termodinámicas y Cero Absoluto

- **Decision**:
  - Constante de Cero Absoluto:
    - Kelvin: $0\text{ K}$
    - Celsius: $-273.15\text{ }^\circ\text{C}$
    - Fahrenheit: $-459.67\text{ }^\circ\text{F}$
  - Conversiones:
    - Celsius ↔ Fahrenheit: $F = (C \times 9/5) + 32$ | $C = (F - 32) \times 5/9$
    - Celsius ↔ Kelvin: $K = C + 273.15$ | $C = K - 273.15$
    - Fahrenheit ↔ Kelvin: $K = (F - 32) \times 5/9 + 273.15$ | $F = (K - 273.15) \times 9/5 + 32$
    - Identidad: Si unidad origen == unidad destino, retornar el valor validado con redondeo a 2 decimales.
  - Validación de Cero Absoluto: Se valida antes de la conversión que el valor de entrada no sea inferior al límite físico de la escala de origen.
- **Rationale**: Corresponde a los estándares internacionales del Sistema Internacional de Unidades (SI) y satisface los criterios de aceptación y casos borde definidos en la especificación.
- **Alternatives considered**:
  - *Validar solo Kelvin*: Dejaría pasar valores imposibles en Celsius (< -273.15 °C) o Fahrenheit (< -459.67 °F). Validar en la escala origen previene estados no físicos desde la entrada.

### 4. Modelo de Manejo de Errores y Excepciones

- **Decision**: Implementar excepciones personalizadas derivadas de `ValueError`:
  - `InvalidTemperatureError`: Entrada no numérica o valor vacío/inválido.
  - `AbsoluteZeroViolationError`: Valor inferior al cero absoluto en la escala especificada.
  - `InvalidScaleError`: Unidad termométrica no reconocida.
  En la interfaz CLI, estas excepciones se capturan para emitir mensajes descriptivos en `stderr` con código de salida `1`, evitando trazas de error (tracebacks) no controladas hacia el usuario final.
- **Rationale**: Permite a los desarrolladores capturar excepciones semánticas específicas programáticamente, mientras provee a los usuarios de la CLI una experiencia limpia y libre de fallos abruptos.
- **Alternatives considered**:
  - *Retornar tuplas `(resultado, error)` o `None`*: Menos idiomático en Python y propenso a omitir comprobaciones de errores.

### 5. Interfaz de Línea de Comandos (CLI)

- **Decision**: Utilizar el módulo estándar `argparse` para la CLI, permitiendo tanto argumentos posicionales simples (`convert-temp <valor> <origen> <destino>`) como banderas opcionales (`--value`, `--from`, `--to`), con soporte insensible a mayúsculas/minúsculas para los símbolos de unidad (`C`, `F`, `K`, `celsius`, `fahrenheit`, `kelvin`).
- **Rationale**: Viene incluido en la biblioteca estándar de Python sin requerir librerías de terceros (Click/Typer), manteniendo el proyecto liviano, rápido y portable.
- **Alternatives considered**:
  - *`sys.argv` manual*: Frágil para manejar flags de ayuda (`-h/--help`) y variaciones en argumentos.
  - *`typer` o `click`*: Requiere dependencias adicionales no justificadas para la escala del problema.

### 6. Estrategia de Pruebas

- **Decision**: Implementar pruebas unitarias, de casos borde y de contrato utilizando `pytest`.
- **Rationale**: `pytest` es el estándar en el ecosistema de Python moderno, se integra fluidamente con `uv` (`uv run pytest`) y permite parametrizar casos de prueba para verificar fácilmente combinaciones de escalas y casos límite.
