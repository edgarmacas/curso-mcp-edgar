# Python API Contract: Convertidor de Temperatura

**Feature**: `001-temperature-converter`
**Status**: Approved

## Módulo: `temperature_converter`

Expone las funciones públicas, clases y excepciones para integración programática.

---

## 1. Función Principal de Conversión

### `convert_temperature`

```python
def convert_temperature(
    value: float | int | str,
    from_scale: str | Scale,
    to_scale: str | Scale,
    precision: int = 2
) -> float:
    """
    Convierte un valor de temperatura entre Celsius, Fahrenheit y Kelvin.

    Args:
        value: Magnitud numérica de la temperatura. Puede suministrarse como float, int o str numérico.
        from_scale: Escala de origen ('C', 'F', 'K' o enum Scale).
        to_scale: Escala objetivo ('C', 'F', 'K' o enum Scale).
        precision: Cantidad de decimales de redondeo (por defecto: 2).

    Returns:
        float: Valor resultante redondeado a `precision` decimales.

    Raises:
        InvalidTemperatureError: Si el valor no es un número finito válido.
        InvalidScaleError: Si la escala de origen o destino no es reconocida.
        AbsoluteZeroViolationError: Si la temperatura es inferior al cero absoluto.
    """
```

---

## 2. Enumeración `Scale`

```python
class Scale(Enum):
    CELSIUS = "C"
    FAHRENHEIT = "F"
    KELVIN = "K"

    @property
    def absolute_zero(self) -> float:
        """Retorna el límite físico inferior en la escala dada."""
        ...

    @classmethod
    def parse(cls, value: str | Scale) -> Scale:
        """Parsea e interpreta de forma tolerante cadenas como 'c', 'celsius', 'C'."""
        ...
```

---

## 3. Jerarquía de Excepciones

```python
class TemperatureConverterError(ValueError):
    """Excepción base para todos los errores del convertidor de temperatura."""
    pass

class InvalidTemperatureError(TemperatureConverterError):
    """Lanzada cuando el valor provisto no es numérico o es NaN/infinito."""
    pass

class InvalidScaleError(TemperatureConverterError):
    """Lanzada cuando la escala especificada no coincide con C, F o K."""
    pass

class AbsoluteZeroViolationError(TemperatureConverterError):
    """Lanzada cuando la temperatura es menor al cero absoluto en la escala de entrada."""
    pass
```

---

## 4. Ejemplos de Uso

```python
from temperature_converter import convert_temperature, Scale, AbsoluteZeroViolationError

# Conversión simple
resultado = convert_temperature(100, "C", "F")
assert resultado == 212.00

# Uso con enums
resultado = convert_temperature(300, Scale.KELVIN, Scale.CELSIUS)
assert resultado == 26.85

# Manejo de error de cero absoluto
try:
    convert_temperature(-500, "F", "C")
except AbsoluteZeroViolationError as e:
    print(f"Error detectado: {e}")
```
