"""Pruebas unitarias para la conversión entre Celsius y Fahrenheit (User Story 1 - P1)."""

import pytest
from temperature_converter import convert_temperature, Scale
from temperature_converter.exceptions import AbsoluteZeroViolationError, InvalidTemperatureError


def test_celsius_to_fahrenheit_freezing_point():
    """0 °C debe convertirse exactamente a 32.00 °F."""
    assert convert_temperature(0, "C", "F") == 32.00


def test_celsius_to_fahrenheit_boiling_point():
    """100 °C debe convertirse exactamente a 212.00 °F."""
    assert convert_temperature(100, "C", "F") == 212.00


def test_celsius_to_fahrenheit_body_temperature():
    """37 °C debe convertirse a 98.60 °F."""
    assert convert_temperature(37, "C", "F") == 98.60


def test_fahrenheit_to_celsius_freezing_point():
    """32 °F debe convertirse a 0.00 °C."""
    assert convert_temperature(32, "F", "C") == 0.00


def test_fahrenheit_to_celsius_boiling_point():
    """212 °F debe convertirse a 100.00 °C."""
    assert convert_temperature(212, "F", "C") == 100.00


def test_celsius_fahrenheit_cross_point():
    """-40 °C debe ser exactamente -40.00 °F y viceversa."""
    assert convert_temperature(-40, "C", "F") == -40.00
    assert convert_temperature(-40, "F", "C") == -40.00


def test_string_numeric_inputs():
    """Valores numéricos pasados como string deben parsearse correctamente."""
    assert convert_temperature("100", "c", "f") == 212.00
    assert convert_temperature("98.6", "fahrenheit", "celsius") == 37.00


def test_rounding_to_two_decimals():
    """Verifica que el redondeo se aplique a 2 decimales."""
    # 1 °C = 33.8 °F -> 33.80
    assert convert_temperature(1, "C", "F") == 33.80
    # 1 °F = -17.2222... °C -> -17.22
    assert convert_temperature(1, "F", "C") == -17.22


def test_scale_enums_supported():
    """Debe permitir el uso del Enum Scale."""
    assert convert_temperature(0, Scale.CELSIUS, Scale.FAHRENHEIT) == 32.00
    assert convert_temperature(32, Scale.FAHRENHEIT, Scale.CELSIUS) == 0.00
