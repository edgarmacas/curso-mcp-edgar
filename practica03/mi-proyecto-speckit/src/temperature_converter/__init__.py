"""Módulo principal del convertidor de temperatura."""

from temperature_converter.converter import convert_temperature
from temperature_converter.exceptions import (
    TemperatureConverterError,
    InvalidTemperatureError,
    InvalidScaleError,
    AbsoluteZeroViolationError,
)
from temperature_converter.models import Scale

__all__ = [
    "convert_temperature",
    "Scale",
    "TemperatureConverterError",
    "InvalidTemperatureError",
    "InvalidScaleError",
    "AbsoluteZeroViolationError",
]
