"""
Suite de pruebas unitarias para el Convertidor de Unidades de Temperatura
Verifica todos los criterios de aceptación y casos borde de spec_manual.md
"""

import unittest
from converter import convert_temperature, parse_temperature_value, normalize_unit


class TestTemperatureConverter(unittest.TestCase):

    # ==========================================
    # Criterio 1: Celsius <-> Fahrenheit
    # ==========================================
    def test_celsius_to_fahrenheit(self):
        self.assertEqual(convert_temperature(0, "C", "F"), 32.0)
        self.assertEqual(convert_temperature(100, "C", "F"), 212.0)
        self.assertEqual(convert_temperature(37, "C", "F"), 98.6)

    def test_fahrenheit_to_celsius(self):
        self.assertEqual(convert_temperature(32, "F", "C"), 0.0)
        self.assertEqual(convert_temperature(212, "F", "C"), 100.0)
        self.assertEqual(convert_temperature(98.6, "F", "C"), 37.0)

    # ==========================================
    # Criterio 2: Celsius <-> Kelvin
    # ==========================================
    def test_celsius_to_kelvin(self):
        self.assertEqual(convert_temperature(0, "C", "K"), 273.15)
        self.assertEqual(convert_temperature(100, "C", "K"), 373.15)
        self.assertEqual(convert_temperature(-273.15, "C", "K"), 0.0)

    def test_kelvin_to_celsius(self):
        self.assertEqual(convert_temperature(273.15, "K", "C"), 0.0)
        self.assertEqual(convert_temperature(373.15, "K", "C"), 100.0)
        self.assertEqual(convert_temperature(0, "K", "C"), -273.15)

    # Conversión adicional: Fahrenheit <-> Kelvin
    def test_fahrenheit_to_kelvin(self):
        self.assertEqual(convert_temperature(32, "F", "K"), 273.15)
        self.assertEqual(convert_temperature(212, "F", "K"), 373.15)

    def test_kelvin_to_fahrenheit(self):
        self.assertEqual(convert_temperature(273.15, "K", "F"), 32.0)
        self.assertEqual(convert_temperature(0, "K", "F"), -459.67)

    # ==========================================
    # Criterio 3: Redondeo a 2 decimales
    # ==========================================
    def test_rounding_to_two_decimals(self):
        # 33 Celsius a Fahrenheit = 91.4
        self.assertEqual(convert_temperature(33, "C", "F"), 91.4)
        # 12.3456 Celsius a Kelvin = 285.4956 -> 285.5
        self.assertEqual(convert_temperature(12.3456, "C", "K"), 285.5)
        # 70 Fahrenheit a Celsius = (70 - 32) * 5 / 9 = 21.111111... -> 21.11
        self.assertEqual(convert_temperature(70, "F", "C"), 21.11)

    # ==========================================
    # Criterio 4: Rechaza Kelvin < 0
    # ==========================================
    def test_reject_negative_kelvin(self):
        with self.assertRaises(ValueError) as ctx:
            convert_temperature(-1, "K", "C")
        self.assertIn("menor a 0 K", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            convert_temperature(-0.01, "K", "F")
        self.assertIn("menor a 0 K", str(ctx.exception))

    def test_reject_below_absolute_zero(self):
        # -300 °C es menor a -273.15 °C (cero absoluto)
        with self.assertRaises(ValueError) as ctx:
            convert_temperature(-300, "C", "K")
        self.assertIn("cero absoluto", str(ctx.exception))

        # -500 °F es menor a -459.67 °F
        with self.assertRaises(ValueError) as ctx:
            convert_temperature(-500, "F", "C")
        self.assertIn("cero absoluto", str(ctx.exception))

    # ==========================================
    # Casos Borde de spec_manual.md
    # ==========================================
    def test_non_numeric_input_raises_clear_error(self):
        invalid_inputs = ["abc", "25a", "", "None", None, [25], {"temp": 20}]
        for val in invalid_inputs:
            with self.assertRaises(ValueError) as ctx:
                convert_temperature(val, "C", "F")
            self.assertTrue(
                "no es un número válido" in str(ctx.exception)
                or "debe ser numérico" in str(ctx.exception)
            )

    def test_same_unit_conversion(self):
        self.assertEqual(convert_temperature(25.5, "C", "C"), 25.5)
        self.assertEqual(convert_temperature(100, "F", "F"), 100.0)
        self.assertEqual(convert_temperature(300.123, "K", "K"), 300.12)
        # Kelvin negativo a Kelvin debe ser rechazado
        with self.assertRaises(ValueError):
            convert_temperature(-5, "K", "K")

    def test_valid_negative_temperatures(self):
        # -40 es el punto de cruce donde C == F
        self.assertEqual(convert_temperature(-40, "C", "F"), -40.0)
        self.assertEqual(convert_temperature(-40, "F", "C"), -40.0)
        self.assertEqual(convert_temperature(-10, "C", "F"), 14.0)
        self.assertEqual(convert_temperature(-10, "F", "C"), -23.33)

    def test_flexible_unit_casing_and_symbols(self):
        self.assertEqual(convert_temperature(100, "celsius", "fahrenheit"), 212.0)
        self.assertEqual(convert_temperature(100, "°C", "°F"), 212.0)
        self.assertEqual(convert_temperature(300, "kelvin", "celsius"), 26.85)

    def test_invalid_unit_raises_error(self):
        with self.assertRaises(ValueError) as ctx:
            convert_temperature(25, "Rankine", "C")
        self.assertIn("no es una unidad válida", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
