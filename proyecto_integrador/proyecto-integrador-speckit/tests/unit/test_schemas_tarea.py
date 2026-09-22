"""Pruebas unitarias para los esquemas DTO de tareas en app/schemas/tarea.py."""

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from app.schemas.tarea import PrioridadEnum, EstadoEnum, TareaCreate, TareaOut, TareaUpdateEstado


def test_tarea_create_valid_and_defaults():
    """Verifica la creación válida de TareaCreate con valores por defecto."""
    tarea = TareaCreate(titulo="Hacer la compra")
    assert tarea.titulo == "Hacer la compra"
    assert tarea.descripcion is None
    assert tarea.prioridad == PrioridadEnum.media
    assert tarea.fecha_limite is None


def test_tarea_create_strip_whitespace():
    """Verifica que los espacios al inicio y final del título se eliminen."""
    tarea = TareaCreate(titulo="   Tarea con espacios   ")
    assert tarea.titulo == "Tarea con espacios"


def test_tarea_create_empty_or_whitespace_only_rejected():
    """Verifica que un título vacío o compuesto solo de espacios sea rechazado."""
    with pytest.raises(ValidationError):
        TareaCreate(titulo="")

    with pytest.raises(ValidationError):
        TareaCreate(titulo="    ")


def test_tarea_create_exceeds_max_length():
    """Verifica que un título mayor a 200 caracteres sea rechazado."""
    with pytest.raises(ValidationError):
        TareaCreate(titulo="A" * 201)


def test_tarea_create_invalid_priority():
    """Verifica que una prioridad que no pertenezca al enum sea rechazada."""
    with pytest.raises(ValidationError):
        TareaCreate(titulo="Tarea", prioridad="urgente")


def test_tarea_out_serialization():
    """Verifica que TareaOut contenga todos los campos de lectura requeridos."""
    now = datetime.now(timezone.utc)
    data = {
        "id": 1,
        "usuario_id": 42,
        "titulo": "Tarea de prueba",
        "descripcion": "Detalles",
        "prioridad": PrioridadEnum.alta,
        "estado": EstadoEnum.en_progreso,
        "fecha_limite": now,
        "creado_en": now,
        "actualizado_en": now,
    }
    out = TareaOut(**data)
    assert out.id == 1
    assert out.usuario_id == 42
    assert out.prioridad == PrioridadEnum.alta
    assert out.estado == EstadoEnum.en_progreso


def test_tarea_update_estado_valid():
    """Verifica la validación correcta de EstadoEnum en TareaUpdateEstado."""
    update = TareaUpdateEstado(estado=EstadoEnum.en_progreso)
    assert update.estado == EstadoEnum.en_progreso


def test_tarea_update_estado_invalid():
    """Verifica que un estado fuera de EstadoEnum sea rechazado."""
    with pytest.raises(ValidationError):
        TareaUpdateEstado(estado="cancelada")

