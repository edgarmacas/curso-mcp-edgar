"""
Convertidor de Unidades de Temperatura
Basado en la especificación: spec_manual.md

Criterios de aceptación:
- Convierte correctamente entre Celsius, Fahrenheit y Kelvin
- Redondea el resultado a 2 decimales
- Rechaza temperaturas en Kelvin menores a 0 (y por debajo del cero absoluto)
- Manejo claro de casos borde (valores no numéricos, misma unidad, valores negativos)
"""

from typing import Union

# Mapeo y normalización de unidades aceptadas
VALID_UNITS = {
    "c": "C",
    "celsius": "C",
    "°c": "C",
    "f": "F",
    "fahrenheit": "F",
    "°f": "F",
    "k": "K",
    "kelvin": "K",
    "°k": "K",
}

UNIT_NAMES = {
    "C": "Celsius (°C)",
    "F": "Fahrenheit (°F)",
    "K": "Kelvin (K)",
}


def normalize_unit(unit: str) -> str:
    """Valida y normaliza el identificador de la unidad a 'C', 'F' o 'K'."""
    if not isinstance(unit, str):
        raise ValueError(
            f"Error de unidad: Se esperaba un texto para la unidad, pero se recibió {type(unit).__name__}."
        )

    cleaned = unit.strip().lower()
    if cleaned not in VALID_UNITS:
        raise ValueError(
            f"Error de unidad: '{unit}' no es una unidad válida. "
            f"Opciones válidas: Celsius ('C'), Fahrenheit ('F'), Kelvin ('K')."
        )
    return VALID_UNITS[cleaned]


def parse_temperature_value(value: Union[int, float, str]) -> float:
    """Valida y parsea el valor numérico de la temperatura."""
    if value is None or isinstance(value, (bool, list, dict, set, tuple)):
        raise ValueError(
            f"Error de entrada: El valor de temperatura debe ser numérico, recibido: {value!r}"
        )

    try:
        val_float = float(value)
    except (ValueError, TypeError):
        raise ValueError(
            f"Error de entrada: El valor '{value}' no es un número válido."
        )

    # Manejar NaN e Infinitos
    if val_float != val_float or abs(val_float) == float("inf"):
        raise ValueError(
            f"Error de entrada: El valor '{value}' no es un número finito válido."
        )

    return val_float


def convert_temperature(
    value: Union[int, float, str],
    from_unit: str,
    to_unit: str
) -> float:
    """
    Convierte una temperatura entre Celsius, Fahrenheit y Kelvin.

    :param value: Valor numérico de la temperatura (int, float o str numérico).
    :param from_unit: Unidad de origen ('C', 'F', 'K' o nombres completos).
    :param to_unit: Unidad de destino ('C', 'F', 'K' o nombres completos).
    :return: Temperatura convertida redondeada a 2 decimales.
    :raises ValueError: Si la entrada no es numérica, la unidad es inválida o
                        la temperatura es inferior al cero absoluto (0 Kelvin).
    """
    # 1. Validar y parsear valor
    num = parse_temperature_value(value)

    # 2. Normalizar unidades
    unit_from = normalize_unit(from_unit)
    unit_to = normalize_unit(to_unit)

    # 3. Validación explícita de Kelvin < 0
    if unit_from == "K" and num < 0:
        raise ValueError(
            f"Error de límite físico: La temperatura en Kelvin no puede ser menor a 0 K. Recibido: {num} K."
        )

    # 4. Caso borde: misma unidad de entrada y salida
    if unit_from == unit_to:
        result = round(num, 2)
        return 0.0 if result == -0.0 else result

    # 5. Conversión a Celsius como temperatura intermedia
    if unit_from == "C":
        celsius = num
    elif unit_from == "F":
        celsius = (num - 32.0) * 5.0 / 9.0
    elif unit_from == "K":
        celsius = num - 273.15
    else:
        raise ValueError(f"Unidad desconocida: {unit_from}")

    # 6. Validar cero absoluto (-273.15 °C = 0 K) con pequeña tolerancia de precisión flotante
    if celsius < -273.15 - 1e-9:
        raise ValueError(
            f"Error de límite físico: La temperatura {num} {unit_from} está por debajo del cero absoluto (0 K / -273.15 °C)."
        )

    # 7. Conversión desde Celsius a la unidad destino
    if unit_to == "C":
        result = celsius
    elif unit_to == "F":
        result = (celsius * 9.0 / 5.0) + 32.0
    elif unit_to == "K":
        result = celsius + 273.15
        # Salvaguarda para asegurar que el resultado en Kelvin nunca sea < 0
        if result < 0:
            raise ValueError(
                f"Error de límite físico: La temperatura resultante en Kelvin sería menor a 0 K."
            )
    else:
        raise ValueError(f"Unidad desconocida: {unit_to}")

    # 8. Redondear a 2 decimales
    rounded = round(result, 2)
    return 0.0 if rounded == -0.0 else rounded


import sys


def main():
    """Interfaz CLI para ejecutar con argumentos o de forma interactiva."""
    args = sys.argv[1:]

    # Si se pasan argumentos: converter.py <valor> <origen> <destino>
    if len(args) == 3:
        raw_val, from_u, to_u = args[0], args[1], args[2]
        try:
            resultado = convert_temperature(raw_val, from_u, to_u)
            u_from_clean = normalize_unit(from_u)
            u_to_clean = normalize_unit(to_u)
            print(f"{raw_val} {UNIT_NAMES[u_from_clean]} = {resultado} {UNIT_NAMES[u_to_clean]}")
        except ValueError as err:
            print(f"❌ {err}", file=sys.stderr)
            sys.exit(1)
        return

    if len(args) in (1, 2) and args[0] in ("-h", "--help"):
        print("Uso:")
        print("  uv run convert_temperature <valor> <unidad_origen> <unidad_destino>")
        print("  uv run converter.py <valor> <unidad_origen> <unidad_destino>")
        print("Ejemplo:")
        print("  uv run convert_temperature 100 C F")
        return

    # Modo interactivo
    print("=" * 60)
    print("🌡️  CONVERTIDOR DE UNIDADES DE TEMPERATURA (C, F, K)")
    print("=" * 60)

    try:
        raw_val = input("Ingresa el valor de temperatura (ej. 25, -40, 100): ").strip()
        from_u = input("Unidad de origen (C, F, K): ").strip()
        to_u = input("Unidad de destino (C, F, K): ").strip()

        resultado = convert_temperature(raw_val, from_u, to_u)
        u_from_clean = normalize_unit(from_u)
        u_to_clean = normalize_unit(to_u)

        print("-" * 60)
        print(f"✅ Resultado: {raw_val} {UNIT_NAMES[u_from_clean]} = {resultado} {UNIT_NAMES[u_to_clean]}")
        print("-" * 60)

    except ValueError as err:
        print(f"\n❌ {err}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario.")


if __name__ == "__main__":
    main()
