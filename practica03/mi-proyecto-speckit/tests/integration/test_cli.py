"""Pruebas de integración para la interfaz de línea de comandos (CLI)."""

import io
from contextlib import redirect_stderr, redirect_stdout
import pytest
from temperature_converter.cli import main


def run_cli_args(args: list[str]) -> tuple[int, str, str]:
    """Ejecuta la función main de la CLI capturando stdout y stderr."""
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
        exit_code = main(args)
    return exit_code, stdout_buf.getvalue(), stderr_buf.getvalue()


def test_cli_positional_arguments_success():
    """Ejecución estándar con argumentos posicionales."""
    code, stdout, stderr = run_cli_args(["100", "C", "F"])
    assert code == 0
    assert stdout.strip() == "212.00"
    assert stderr == ""


def test_cli_named_flags_success():
    """Ejecución con banderas con nombre --value, --from, --to."""
    code, stdout, stderr = run_cli_args(["--value", "0", "--from", "C", "--to", "K"])
    assert code == 0
    assert stdout.strip() == "273.15"
    assert stderr == ""


def test_cli_identity():
    """Ejecución de identidad devuelve el mismo valor con 2 decimales."""
    code, stdout, stderr = run_cli_args(["25", "C", "C"])
    assert code == 0
    assert stdout.strip() == "25.00"


def test_cli_missing_arguments():
    """Falta de argumentos debe retornar código 1 y mensaje en stderr."""
    code, stdout, stderr = run_cli_args(["100", "C"])
    assert code == 1
    assert "Error: Se requieren tres parámetros" in stderr


def test_cli_non_numeric_error():
    """Entrada no numérica debe retornar código 1 y mensaje amigable en stderr."""
    code, stdout, stderr = run_cli_args(["abc", "C", "F"])
    assert code == 1
    assert "no es un número válido" in stderr


def test_cli_absolute_zero_violation():
    """Violación de cero absoluto debe retornar código 1 y mensaje claro en stderr."""
    code, stdout, stderr = run_cli_args(["-10", "K", "C"])
    assert code == 1
    assert "cero absoluto" in stderr.lower()


def test_cli_invalid_scale():
    """Escala no soportada debe retornar código 1 y mensaje en stderr."""
    code, stdout, stderr = run_cli_args(["100", "X", "C"])
    assert code == 1
    assert "Escala desconocida" in stderr


def test_cli_interactive_mode_success(monkeypatch):
    """Ejecución en modo interactivo sin argumentos respondiendo a los inputs."""
    import sys
    inputs = iter(["100", "C", "F"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    code, stdout, stderr = run_cli_args([])
    assert code == 0
    assert "212.00 F" in stdout
    assert stderr == ""

