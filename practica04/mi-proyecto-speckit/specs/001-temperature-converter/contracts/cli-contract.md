# CLI Interface Contract: Convertidor de Temperatura

**Feature**: `001-temperature-converter`
**Status**: Approved

## Descripción General

La interfaz de línea de comandos proporciona acceso directo al motor de conversión de temperatura para usuarios de terminal, scripts de shell y automatizaciones.

---

## Sintaxis de Ejecución

```bash
# Invocación directa mediante módulo Python con argumentos
python -m temperature_converter <valor> <origen> <destino>

# Invocación en modo interactivo guiado por consola
python -m temperature_converter
# o explícitamente:
python -m temperature_converter --interactive / -i

# O mediante comando de proyecto si está instalado
convert-temp <valor> <origen> <destino>
convert-temp  # lanza modo interactivo
```

Soporte opcional con banderas nombradas:

```bash
python -m temperature_converter --value <valor> --from <origen> --to <destino>
```

---

## Parámetros

| Parámetro | Tipo | Requerido | Descripción | Ejemplos |
|---|---|:---:|---|---|
| `<valor>` / `--value` | Decimal / Float | Sí | Magnitud numérica de la temperatura a convertir | `100`, `32.5`, `-40`, `0` |
| `<origen>` / `--from` | Cadena | Sí | Escala termométrica de entrada (insensible a mayúsculas) | `C`, `F`, `K`, `celsius`, `fahrenheit`, `kelvin` |
| `<destino>` / `--to` | Cadena | Sí | Escala termométrica objetivo (insensible a mayúsculas) | `C`, `F`, `K`, `celsius`, `fahrenheit`, `kelvin` |

---

## Códigos de Salida (Exit Codes)

| Código | Significado | Salida Estándar (`stdout`) | Salida de Error (`stderr`) |
|:---:|---|---|---|
| `0` | Éxito | Resultado numérico formateado a 2 decimales | Vacío |
| `1` | Error de validación o entrada (no numérico, unidad inválida, debajo de cero absoluto) | Vacío | Mensaje de error claro y descriptivo |
| `2` | Argumentos insuficientes o sintaxis de comando incorrecta | Vacío | Uso de comando / ayuda generada por argparse |

---

## Ejemplos de Interacción

### 1. Casos Exitosos (`exit code 0`)

```bash
$ python -m temperature_converter 100 C F
212.00

$ python -m temperature_converter 0 C K
273.15

$ python -m temperature_converter 32 F C
0.00

$ python -m temperature_converter -40 C F
-40.00

$ python -m temperature_converter 25 C C
25.00
```

### 2. Casos de Error (`exit code 1` - Salida en `stderr`)

**Entrada no numérica:**
```bash
$ python -m temperature_converter abc C F
Error: El valor 'abc' no es un número válido.
```

**Violación de cero absoluto:**
```bash
$ python -m temperature_converter -10 K C
Error: La temperatura -10.00 K está por debajo del cero absoluto (mínimo: 0.00 K).

$ python -m temperature_converter -300 C K
Error: La temperatura -300.00 °C está por debajo del cero absoluto (mínimo: -273.15 °C).
```

**Unidad inválida:**
```bash
$ python -m temperature_converter 100 X C
Error: Escala desconocida 'X'. Escalas válidas: C, F, K.
```
