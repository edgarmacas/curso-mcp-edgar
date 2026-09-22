import pytest
from app.schemas.tarea import PrioridadEnum, EstadoEnum


def test_prioridad_enum_values():
    assert PrioridadEnum.baja == "baja"
    assert PrioridadEnum.media == "media"
    assert PrioridadEnum.alta == "alta"
    assert len(PrioridadEnum) == 3

    with pytest.raises(ValueError):
        PrioridadEnum("urgente")


def test_estado_enum_values():
    assert EstadoEnum.pendiente == "pendiente"
    assert EstadoEnum.en_progreso == "en_progreso"
    assert EstadoEnum.completada == "completada"
    assert len(EstadoEnum) == 3

    with pytest.raises(ValueError):
        EstadoEnum("cancelada")
