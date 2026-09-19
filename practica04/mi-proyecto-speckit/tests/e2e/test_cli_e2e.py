"""Pruebas end-to-end (proceso completo vía subprocess) para la CLI."""

import subprocess
import sys


def test_e2e_cli_conversion_success():
    """Prueba E2E ejecutando el proceso completo de conversión."""
    result = subprocess.run(
        [sys.executable, "-m", "temperature_converter", "100", "C", "F"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "212.00" in result.stdout


def test_e2e_cli_invalid_unit_failure():
    """Prueba E2E verificando que una unidad inválida retorne código de error."""
    result = subprocess.run(
        [sys.executable, "-m", "temperature_converter", "100", "X", "F"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
