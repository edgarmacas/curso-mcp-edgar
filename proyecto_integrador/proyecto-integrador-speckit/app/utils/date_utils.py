"""Utilidades puras de fecha y normalización temporal sin dependencias de dominio."""

from datetime import datetime, timezone
from typing import Optional


def now_utc() -> datetime:
    """Retorna la fecha y hora actual en UTC."""
    return datetime.now(timezone.utc)


def to_iso_utc(dt: Optional[datetime]) -> Optional[str]:
    """Convierte un objeto datetime a cadena ISO-8601 con sufijo Z."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parsea una cadena ISO-8601 a un datetime consciente de zona horaria UTC."""
    if not value or not value.strip():
        return None
    clean_val = value.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(clean_val)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt
