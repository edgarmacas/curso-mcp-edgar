"""Modelos de dominio y definición de escalas termométricas."""

from enum import Enum
from typing import Self
from temperature_converter.exceptions import InvalidScaleError


class Scale(str, Enum):
    """Escalas termométricas soportadas por el convertidor."""

    CELSIUS = "C"
    FAHRENHEIT = "F"
    KELVIN = "K"

    @property
    def absolute_zero(self) -> float:
        """Retorna el límite físico inferior (cero absoluto) en la escala actual."""
        match self:
            case Scale.CELSIUS:
                return -273.15
            case Scale.FAHRENHEIT:
                return -459.67
            case Scale.KELVIN:
                return 0.0

    @property
    def symbol(self) -> str:
        """Símbolo estándar de la unidad termométrica."""
        match self:
            case Scale.CELSIUS:
                return "°C"
            case Scale.FAHRENHEIT:
                return "°F"
            case Scale.KELVIN:
                return "K"

    @classmethod
    def parse(cls, value: Self | str) -> "Scale":
        """
        Normaliza e interpreta cadenas de texto como escalas válidas.

        Acepta variantes como 'c', 'C', 'celsius', '°c', 'f', 'fahrenheit', 'k', 'kelvin'.
        Lanza InvalidScaleError si no se reconoce la escala.
        """
        if isinstance(value, cls):
            return value

        if not isinstance(value, str):
            raise InvalidScaleError(f"Tipo de escala inválido: {type(value).__name__}. Se esperaba str o Scale.")

        normalized = value.strip().lower()
        # Normalizar símbolos comunes
        normalized = normalized.lstrip("°").strip()

        match normalized:
            case "c" | "celsius":
                return cls.CELSIUS
            case "f" | "fahrenheit":
                return cls.FAHRENHEIT
            case "k" | "kelvin":
                return cls.KELVIN
            case _:
                raise InvalidScaleError(
                    f"Escala desconocida '{value}'. Las escalas válidas son: C (Celsius), F (Fahrenheit), K (Kelvin)."
                )
