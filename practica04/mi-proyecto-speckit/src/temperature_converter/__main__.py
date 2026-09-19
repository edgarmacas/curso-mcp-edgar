"""Punto de entrada para ejecución directa del módulo vía `python -m temperature_converter`."""

import sys
from temperature_converter.cli import main

if __name__ == "__main__":
    sys.exit(main())
