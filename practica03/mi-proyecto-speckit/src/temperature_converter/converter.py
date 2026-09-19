"""Lógica central de conversión termodinámica y validación de temperatura."""

import math
from temperature_converter.exceptions import (
    AbsoluteZeroViolationError,
    InvalidScaleError,
    InvalidTemperatureError,
)
from temperature_converter.models import Scale


def _parse_numeric_value(value: float | int | str) -> float:
    """Parsea y valida que el valor sea un número real finito."""
    if value is None:
        raise InvalidTemperatureError("El valor de temperatura no puede ser nulo o vacío.")

    if isinstance(value, (int, float)):
        val = float(value)
    elif isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise InvalidTemperatureError("El valor de temperatura no puede ser una cadena vacía.")
        try:
            val = float(stripped)
        except ValueError:
            raise InvalidTemperatureError(f"El valor '{value}' no es un número válido.")
    else:
        raise InvalidTemperatureError(
            f"Tipo de valor no soportado: '{type(value).__name__}'. Se esperaba un número o cadena numérica."
        )

    if math.isnan(val) or math.isinf(val):
        raise InvalidTemperatureError(f"El valor '{value}' no es un número finito permitido.")

    return val


def convert_temperature(
    value: float | int | str,
    from_scale: str | Scale,
    to_scale: str | Scale,
    precision: int = 2,
) -> float:
    """
    Convierte una temperatura entre las escalas Celsius, Fahrenheit y Kelvin.

    Args:
        value: Magnitud numérica de la temperatura.
        from_scale: Escala de origen (str o enum Scale).
        to_scale: Escala objetivo (str o enum Scale).
        precision: Lugares decimales de redondeo (por defecto: 2).

    Returns:
        float: Temperatura convertida redondeada a `precision` decimales.

    Raises:
        InvalidTemperatureError: Si el valor no es numérico o es NaN/infinito.
        InvalidScaleError: Si la escala de origen o destino no es reconocida.
        AbsoluteZeroViolationError: Si la temperatura está por debajo del cero absoluto.
    """
    # 1. Parseo y validación de tipo del valor numérico
    num_value = _parse_numeric_value(value)

    # 2. Parseo y normalización de escalas
    src_scale = Scale.parse(from_scale)
    dest_scale = Scale.parse(to_scale)

    # 3. Validación de límite físico (Cero Absoluto en escala de origen)
    if num_value < src_scale.absolute_zero:
        raise AbsoluteZeroViolationError(
            f"La temperatura {num_value:.2f} {src_scale.symbol} está por debajo del "
            f"cero absoluto (mínimo permitido: {src_scale.absolute_zero:.2f} {src_scale.symbol})."
        )

    # 4. Caso de identidad
    if src_scale == dest_scale:
        return round(num_value, precision)

    # 5. Cálculo termodinámico según origen y destino
    match (src_scale, dest_scale):
        # Celsius <-> Fahrenheit
        case (Scale.CELSIUS, Scale.FAHRENHEIT):
            converted = (num_value * 9.0 / 5.0) + 32.0
        case (Scale.FAHRENHEIT, Scale.CELSIUS):
            converted = (num_value - 32.0) * 5.0 / 9.0

        # Celsius <-> Kelvin
        case (Scale.CELSIUS, Scale.KELVIN):
            converted = num_value + 273.15
        case (Scale.KELVIN, Scale.CELSIUS):
            converted = num_value - 273.15

        # Fahrenheit <-> Kelvin
        case (Scale.FAHRENHEIT, Scale.KELVIN):
            converted = (num_value - 32.0) * 5.0 / 9.0 + 273.15
        case (Scale.KELVIN, Scale.FAHRENHEIT):
            converted = (num_value - 273.15) * 9.0 / 5.0 + 32.0

        case _:
            raise InvalidScaleError(f"Conversión no soportada de {src_scale} a {dest_scale}.")

    # 6. Redondeo final
    return round(converted, precision)
