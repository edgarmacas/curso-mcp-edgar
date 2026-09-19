"""Pruebas unitarias para conversiones de identidad (misma escala origen y destino, US4 - P4)."""

import pytest
from temperature_converter import convert_temperature, Scale
from temperature_converter.exceptions import AbsoluteZeroViolationError


def test_celsius_identity():
    """Celsius a Celsius debe devolver el mismo valor redondeado a 2 decimales."""
    assert convert_temperature(25, "C", "C") == 25.00
    assert convert_temperature(-40, "celsius", "c") == -40.00
    assert convert_temperature(12.3456, "C", "C") == 12.35


def test_fahrenheit_identity():
    """Fahrenheit a Fahrenheit debe devolver el mismo valor."""
    assert convert_temperature(32, "F", "F") == 32.00
    assert convert_temperature(98.6, "fahrenheit", "F") == 98.60


def test_kelvin_identity():
    """Kelvin a Kelvin debe devolver el mismo valor."""
    assert convert_temperature(0, "K", "K") == 0.00
    assert convert_temperature(273.15, "kelvin", "k") == 273.15


def test_identity_still_enforces_absolute_zero():
    """Incluso en conversiones de identidad, se debe validar el cero absoluto."""
    with pytest.raises(AbsoluteZeroViolationError):
        convert_temperature(-5, "K", "K")

    with pytest.raises(AbsoluteZeroViolationError):
        convert_temperature(-300, "C", "C")
