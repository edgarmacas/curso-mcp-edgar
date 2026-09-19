"""Pruebas unitarias para la conversión entre Fahrenheit y Kelvin (US3 - P3)."""

import pytest
from temperature_converter import convert_temperature, Scale
from temperature_converter.exceptions import AbsoluteZeroViolationError


def test_fahrenheit_to_kelvin_freezing():
    """32 °F debe convertirse a 273.15 K."""
    assert convert_temperature(32, "F", "K") == 273.15


def test_fahrenheit_to_kelvin_boiling():
    """212 °F debe convertirse a 373.15 K."""
    assert convert_temperature(212, "F", "K") == 373.15


def test_kelvin_to_fahrenheit_freezing():
    """273.15 K debe convertirse a 32.00 °F."""
    assert convert_temperature(273.15, "K", "F") == 32.00


def test_kelvin_to_fahrenheit_boiling():
    """373.15 K debe convertirse a 212.00 °F."""
    assert convert_temperature(373.15, "K", "F") == 212.00


def test_absolute_zero_fahrenheit_to_kelvin():
    """-459.67 °F debe ser 0.00 K."""
    assert convert_temperature(-459.67, "F", "K") == 0.00


def test_absolute_zero_kelvin_to_fahrenheit():
    """0 K debe ser -459.67 °F."""
    assert convert_temperature(0, "K", "F") == -459.67


def test_below_absolute_zero_fahrenheit_raises_violation():
    """Valores por debajo de -459.67 °F deben lanzar AbsoluteZeroViolationError."""
    with pytest.raises(AbsoluteZeroViolationError):
        convert_temperature(-459.68, "F", "K")

    with pytest.raises(AbsoluteZeroViolationError):
        convert_temperature(-500, "F", "K")
