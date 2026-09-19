# Quickstart & Validation Guide: Convertidor de Temperatura

**Feature**: `001-temperature-converter`
**Status**: Ready for Validation

Esta guía detalla los pasos y comandos para validar la funcionalidad del convertidor de temperatura de extremo a extremo una vez implementado.

---

## Prerrequisitos

- Python 3.12+ instalado
- Herramienta de gestión `uv` instalada

---

## 1. Configuración del Entorno

Desde la raíz del proyecto (`mi-proyecto-speckit`):

```bash
# Sincronizar o instalar entorno virtual y dependencias de desarrollo
uv sync
```

---

## 2. Escenarios de Validación Rápida (End-to-End)

### Escenario 1: Conversión Estándar (Celsius a Fahrenheit)
- **Comando**:
  ```bash
  uv run python -m temperature_converter 100 C F
  ```
- **Resultado Esperado**:
  - Salida: `212.00`
  - Código de salida: `0`

### Escenario 2: Conversión a Kelvin (Celsius a Kelvin)
- **Comando**:
  ```bash
  uv run python -m temperature_converter 0 C K
  ```
- **Resultado Esperado**:
  - Salida: `273.15`
  - Código de salida: `0`

### Escenario 3: Conversión de Identidad (Misma escala origen y destino)
- **Comando**:
  ```bash
  uv run python -m temperature_converter 25 C C
  ```
- **Resultado Esperado**:
  - Salida: `25.00`
  - Código de salida: `0`

### Escenario 4: Validación de Cero Absoluto (Kelvin menor a cero)
- **Comando**:
  ```bash
  uv run python -m temperature_converter -5 K C
  ```
- **Resultado Esperado**:
  - Código de salida: `1`
  - Mensaje en `stderr` indicando que el valor está por debajo del cero absoluto.

### Escenario 5: Validación de Entrada No Numérica
- **Comando**:
  ```bash
  uv run python -m temperature_converter abc C F
  ```
- **Resultado Esperado**:
  - Código de salida: `1`
  - Mensaje en `stderr` indicando que la entrada no es un valor numérico válido.

---

## 3. Ejecución de la Suite de Pruebas Automatizadas

```bash
# Ejecutar todas las pruebas unitarias y de integración con pytest
uv run pytest -v
```

**Criterio de éxito**: 100% de las pruebas pasan sin fallos.
