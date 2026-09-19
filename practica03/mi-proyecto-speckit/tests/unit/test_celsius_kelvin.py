"""Pruebas unitarias para la conversión entre Celsius y Kelvin y validación de cero absoluto (US2 - P2)."""

import pytest
from temperature_converter import convert_temperature, Scale
from temperature_converter.exceptions import AbsoluteZeroViolationError


def test_celsius_to_kelvin_freezing():
    """0 °C debe convertirse a 273.15 K."""
    assert convert_temperature(0, "C", "K") == 273.15


def test_celsius_to_kelvin_boiling():
    """100 °C debe convertirse a 373.15 K."""
    assert convert_temperature(100, "C", "K") == 373.15


def test_kelvin_to_celsius():
    """300 K debe convertirse a 26.85 °C."""
    assert convert_temperature(300, "K", "C") == 26.85


def test_absolute_zero_celsius_to_kelvin():
    """-273.15 °C debe ser exactamente 0.00 K."""
    assert convert_temperature(-273.15, "C", "K") == 0.00


def test_absolute_zero_kelvin_to_celsius():
    """0 K debe ser exactamente -273.15 °C."""
    assert convert_temperature(0, "K", "C") == -273.15


def test_negative_kelvin_raises_violation():
    """Cualquier valor menor a 0 Kelvin debe lanzar AbsoluteZeroViolationError."""
    with pytest.raises(AbsoluteZeroViolationError) as exc_info:
        convert_temperature(-0.01, "K", "C")
    assert "cero absoluto" in str(exc_info.value).lower()

    with pytest.raises(AbsoluteZeroViolationError) as exc_info:
        convert_temperature(-10, "K", "C")
    assert "cero absoluto" in str(exc_info.value).lower()


def test_below_absolute_zero_in_celsius_raises_violation():
    """Valores por debajo de -273.15 °C deben rechazarse."""
    with pytest.raises(AbsoluteZeroViolationError) as exc_info:
        convert_temperature(-273.16, "C", "K")
    assert "cero absoluto" in str(exc_info.value).lower()


def test_kelvin_case_insensitivity():
    """Las unidades deben ser insensibles a mayúsculas y minúsculas."""
    assert convert_temperature("0", "kelvin", "celsius") == -273.15
    assert convert_temperature("273.15", "k", "c") == 0.00
