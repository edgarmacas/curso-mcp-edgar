"""Interfaz de línea de comandos para el convertidor de temperatura."""

import argparse
import sys
from temperature_converter.converter import convert_temperature
from temperature_converter.exceptions import TemperatureConverterError


def create_parser() -> argparse.ArgumentParser:
    """Crea y configura el analizador de argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        prog="convert-temp",
        description="Convierte temperaturas entre Celsius (C), Fahrenheit (F) y Kelvin (K).",
    )

    parser.add_argument(
        "value",
        nargs="?",
        default=None,
        help="Valor numérico de la temperatura a convertir.",
    )
    parser.add_argument(
        "from_scale",
        nargs="?",
        default=None,
        help="Escala de origen: C, F, K.",
    )
    parser.add_argument(
        "to_scale",
        nargs="?",
        default=None,
        help="Escala de destino: C, F, K.",
    )

    # Soporte para banderas con nombre
    parser.add_argument("--value", dest="flag_value", help="Valor numérico de la temperatura.")
    parser.add_argument("--from", dest="flag_from", help="Escala de origen (C, F, K).")
    parser.add_argument("--to", dest="flag_to", help="Escala de destino (C, F, K).")
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Ejecutar en modo interactivo guiado por consola.",
    )
    parser.add_argument(
        "--precision",
        type=int,
        default=2,
        help="Cantidad de decimales para el resultado (por defecto: 2).",
    )

    return parser


def run_interactive(precision: int = 2) -> int:
    """Modo interactivo en consola para pedir datos paso a paso al usuario."""
    print("=" * 60)
    print("🌡️  CONVERTIDOR DE TEMPERATURA (Celsius, Fahrenheit, Kelvin)")
    print("=" * 60)

    try:
        raw_val = input("Ingresa el valor de temperatura (ej. 100, -40, 25): ").strip()
        src_scale = input("Escala de origen (C, F, K): ").strip()
        dest_scale = input("Escala de destino (C, F, K): ").strip()

        resultado = convert_temperature(
            value=raw_val,
            from_scale=src_scale,
            to_scale=dest_scale,
            precision=precision,
        )
        print("-" * 60)
        print(f"✅ Resultado: {raw_val} {src_scale.upper()} = {resultado:.2f} {dest_scale.upper()}")
        print("-" * 60)
        return 0
    except TemperatureConverterError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print("\nOperación cancelada.")
        return 1


def main(args: list[str] | None = None) -> int:
    """Punto de entrada principal para la ejecución de la CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    raw_val = parsed_args.value if parsed_args.value is not None else parsed_args.flag_value
    src_scale = parsed_args.from_scale if parsed_args.from_scale is not None else parsed_args.flag_from
    dest_scale = parsed_args.to_scale if parsed_args.to_scale is not None else parsed_args.flag_to

    # Si se solicitó explícitamente modo interactivo o no se proporcionó ningún argumento
    if parsed_args.interactive or (raw_val is None and src_scale is None and dest_scale is None):
        return run_interactive(precision=parsed_args.precision)

    # Si se pasaron solo algunos argumentos incompletos
    if raw_val is None or src_scale is None or dest_scale is None:
        parser.print_usage(sys.stderr)
        print("Error: Se requieren tres parámetros: valor, escala origen y escala destino.", file=sys.stderr)
        return 1

    try:
        resultado = convert_temperature(
            value=raw_val,
            from_scale=src_scale,
            to_scale=dest_scale,
            precision=parsed_args.precision,
        )
        print(f"{resultado:.2f}")
        return 0
    except TemperatureConverterError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
