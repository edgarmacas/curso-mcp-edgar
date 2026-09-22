"""Pruebas unitarias para el modelo ORM Tarea."""

from app.models.usuario import Usuario
from app.models.tarea import Tarea
from app.schemas.tarea import PrioridadEnum, EstadoEnum


def test_create_and_query_tarea(db_session):
    """Verifica la persistencia de una Tarea vinculada a un Usuario y sus valores por defecto."""
    usuario = Usuario(
        email="owner@example.com",
        password_hash="hash123456",
    )
    db_session.add(usuario)
    db_session.commit()

    tarea = Tarea(
        usuario_id=usuario.id,
        titulo="Completar integracion",
        descripcion="Detalle de la tarea",
    )
    db_session.add(tarea)
    db_session.commit()
    db_session.refresh(tarea)

    assert tarea.id is not None
    assert tarea.usuario_id == usuario.id
    assert tarea.titulo == "Completar integracion"
    assert tarea.prioridad == PrioridadEnum.media
    assert tarea.estado == EstadoEnum.pendiente
    assert tarea.creado_en is not None
    assert tarea.actualizado_en is not None
    assert tarea.usuario.email == "owner@example.com"
    assert len(usuario.tareas) == 1


def test_cascade_delete_tarea_when_usuario_deleted(db_session):
    """Verifica que al eliminar un Usuario se eliminen sus tareas asociadas (cascade)."""
    usuario = Usuario(
        email="to_delete@example.com",
        password_hash="hash123456",
    )
    db_session.add(usuario)
    db_session.commit()

    tarea = Tarea(
        usuario_id=usuario.id,
        titulo="Tarea por borrar",
    )
    db_session.add(tarea)
    db_session.commit()

    tarea_id = tarea.id
    db_session.delete(usuario)
    db_session.commit()

    tarea_consultada = db_session.query(Tarea).filter(Tarea.id == tarea_id).first()
    assert tarea_consultada is None
