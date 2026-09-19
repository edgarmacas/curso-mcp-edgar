"""Excepciones de dominio para el convertidor de temperatura."""


class TemperatureConverterError(ValueError):
    """Excepción base para todos los errores del convertidor de temperatura."""
    pass


class InvalidTemperatureError(TemperatureConverterError):
    """Lanzada cuando el valor provisto no es numérico, está vacío o es NaN/infinito."""
    pass


class InvalidScaleError(TemperatureConverterError):
    """Lanzada cuando la escala especificada no coincide con C, F o K."""
    pass


class AbsoluteZeroViolationError(TemperatureConverterError):
    """Lanzada cuando la temperatura es menor al cero absoluto en la escala especificada."""
    pass
