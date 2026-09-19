"""Pruebas de casos borde y robustez para el convertidor de temperatura."""

import pytest
from temperature_converter import convert_temperature, Scale
from temperature_converter.exceptions import (
    AbsoluteZeroViolationError,
    InvalidScaleError,
    InvalidTemperatureError,
)


def test_empty_string_value():
    """Valores vacíos o con solo espacios deben lanzar InvalidTemperatureError."""
    with pytest.raises(InvalidTemperatureError):
        convert_temperature("", "C", "F")

    with pytest.raises(InvalidTemperatureError):
        convert_temperature("   ", "C", "F")


def test_alphanumeric_and_special_chars_value():
    """Valores con texto alfanumérico o caracteres especiales deben ser rechazados."""
    for invalid_val in ["abc", "12a", "twenty", "$100", "10,5"]:
        with pytest.raises(InvalidTemperatureError):
            convert_temperature(invalid_val, "C", "F")


def test_nan_and_infinity_rejected():
    """Valores especiales flotantes NaN e Infinito deben ser rechazados."""
    for special in [float("nan"), float("inf"), float("-inf"), "nan", "inf"]:
        with pytest.raises(InvalidTemperatureError):
            convert_temperature(special, "C", "F")


def test_whitespace_tolerance():
    """Debe tolerar espacios en blanco alrededor de números y escalas."""
    assert convert_temperature("  100  ", "  c  ", "  f  ") == 212.00
    assert convert_temperature(" 0 ", " C ", " K ") == 273.15


def test_degree_symbol_tolerance():
    """Debe aceptar símbolos de grado habituales (°C, °F)."""
    assert convert_temperature(100, "°C", "°F") == 212.00
    assert convert_temperature(32, "°F", "°C") == 0.00


def test_invalid_scale_names():
    """Escalas desconocidas deben lanzar InvalidScaleError con mensaje claro."""
    for bad_scale in ["Rankine", "R", "X", "unknown", "123"]:
        with pytest.raises(InvalidScaleError) as exc_info:
            convert_temperature(100, bad_scale, "C")
        assert "Escala desconocida" in str(exc_info.value)


def test_high_precision_rounding():
    """Verifica que números con infinitos decimales se redondeen estrictamente a 2 decimales."""
    # 100 F a C = (100 - 32) * 5/9 = 68 * 5/9 = 37.7777777... -> 37.78
    assert convert_temperature(100, "F", "C") == 37.78

    # 1 F a C = (1 - 32) * 5/9 = -31 * 5/9 = -17.22222... -> -17.22
    assert convert_temperature(1, "F", "C") == -17.22


def test_large_temperature_values():
    """Temperaturas muy altas (ej. fotosfera solar 5778 K) deben procesarse con precisión."""
    assert convert_temperature(5778, "K", "C") == 5504.85
    assert convert_temperature(5504.85, "C", "K") == 5778.00


def test_exact_absolute_zero_boundary():
    """Comprueba el límite exacto del cero absoluto en todas las escalas."""
    # En Kelvin
    assert convert_temperature(0.0, "K", "C") == -273.15
    with pytest.raises(AbsoluteZeroViolationError):
        convert_temperature(-0.0001, "K", "C")

    # En Celsius
    assert convert_temperature(-273.15, "C", "K") == 0.00
    with pytest.raises(AbsoluteZeroViolationError):
        convert_temperature(-273.16, "C", "K")

    # En Fahrenheit
    assert convert_temperature(-459.67, "F", "K") == 0.00
    with pytest.raises(AbsoluteZeroViolationError):
        convert_temperature(-459.68, "F", "K")
