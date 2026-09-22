"""Pruebas de integración para TareasRepository en app/repositories/tareas_repository.py."""

from app.models.usuario import Usuario
from app.schemas.tarea import PrioridadEnum, EstadoEnum, TareaCreate
from app.repositories.tareas_repository import TareasRepository


def _crear_usuario(db, email="repo_user@example.com"):
    usuario = Usuario(email=email, password_hash="hash123")
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def test_crear_tarea_y_contar_abiertas_por_prioridad(db_session):
    """Verifica crear_tarea y el conteo de tareas abiertas por prioridad con aislamiento por usuario."""
    repo = TareasRepository()
    usuario1 = _crear_usuario(db_session, "user1@example.com")
    usuario2 = _crear_usuario(db_session, "user2@example.com")

    # Crear 2 tareas de prioridad alta para usuario1 (ambas pendientes por defecto)
    t1 = repo.crear_tarea(
        datos=TareaCreate(titulo="Tarea Alta 1", prioridad=PrioridadEnum.alta),
        usuario_id=usuario1.id,
        db=db_session,
    )
    t2 = repo.crear_tarea(
        datos=TareaCreate(titulo="Tarea Alta 2", prioridad=PrioridadEnum.alta),
        usuario_id=usuario1.id,
        db=db_session,
    )
    # Crear 1 tarea media para usuario1
    repo.crear_tarea(
        datos=TareaCreate(titulo="Tarea Media 1", prioridad=PrioridadEnum.media),
        usuario_id=usuario1.id,
        db=db_session,
    )
    # Crear 1 tarea alta para usuario2
    repo.crear_tarea(
        datos=TareaCreate(titulo="Tarea Alta User2", prioridad=PrioridadEnum.alta),
        usuario_id=usuario2.id,
        db=db_session,
    )

    # Conteo para usuario 1
    assert repo.contar_abiertas_por_prioridad(usuario1.id, PrioridadEnum.alta, db=db_session) == 2
    assert repo.contar_abiertas_por_prioridad(usuario1.id, PrioridadEnum.media, db=db_session) == 1
    assert repo.contar_abiertas_por_prioridad(usuario1.id, PrioridadEnum.baja, db=db_session) == 0

    # Si t1 se completa, ya no debe contar como abierta
    repo.actualizar_estado(t1.id, usuario1.id, EstadoEnum.completada, db=db_session)
    assert repo.contar_abiertas_por_prioridad(usuario1.id, PrioridadEnum.alta, db=db_session) == 1

    # Si t2 se mueve a en_progreso, sigue contando como abierta
    repo.actualizar_estado(t2.id, usuario1.id, EstadoEnum.en_progreso, db=db_session)
    assert repo.contar_abiertas_por_prioridad(usuario1.id, PrioridadEnum.alta, db=db_session) == 1

    # Conteo para usuario 2 no debe estar contaminado
    assert repo.contar_abiertas_por_prioridad(usuario2.id, PrioridadEnum.alta, db=db_session) == 1


def test_obtener_y_eliminar_tarea(db_session):
    """Verifica aislamiento en obtener_por_id, buscar_por_id_global y eliminar_tarea."""
    repo = TareasRepository()
    usuario1 = _crear_usuario(db_session, "userA@example.com")
    usuario2 = _crear_usuario(db_session, "userB@example.com")

    tarea = repo.crear_tarea(
        datos=TareaCreate(titulo="Tarea Privada", prioridad=PrioridadEnum.baja),
        usuario_id=usuario1.id,
        db=db_session,
    )

    # Usuario 1 puede obtenerla por ID
    assert repo.obtener_por_id(tarea.id, usuario1.id, db=db_session) is not None

    # Usuario 2 no puede obtenerla por su usuario_id (retorna None)
    assert repo.obtener_por_id(tarea.id, usuario2.id, db=db_session) is None

    # Búsqueda global la encuentra
    assert repo.buscar_por_id_global(tarea.id, db=db_session) is not None

    # Eliminar tarea con usuario incorrecto falla
    assert repo.eliminar_tarea(tarea.id, usuario2.id, db=db_session) is False
    # Eliminar tarea con propietario tiene éxito
    assert repo.eliminar_tarea(tarea.id, usuario1.id, db=db_session) is True
    assert repo.buscar_por_id_global(tarea.id, db=db_session) is None


def test_contar_por_estado_aislado(db_session):
    """Verifica que contar_por_estado cuente con exactitud y aislamiento por usuario."""
    repo = TareasRepository()
    usuario1 = _crear_usuario(db_session, "state_user1@example.com")
    usuario2 = _crear_usuario(db_session, "state_user2@example.com")

    # Crear 3 tareas para usuario 1
    t1 = repo.crear_tarea(datos=TareaCreate(titulo="T1"), usuario_id=usuario1.id, db=db_session)
    t2 = repo.crear_tarea(datos=TareaCreate(titulo="T2"), usuario_id=usuario1.id, db=db_session)
    t3 = repo.crear_tarea(datos=TareaCreate(titulo="T3"), usuario_id=usuario1.id, db=db_session)

    # Crear 1 tarea para usuario 2
    repo.crear_tarea(datos=TareaCreate(titulo="T4"), usuario_id=usuario2.id, db=db_session)

    assert repo.contar_por_estado(usuario1.id, EstadoEnum.pendiente, db=db_session) == 3
    assert repo.contar_por_estado(usuario1.id, EstadoEnum.en_progreso, db=db_session) == 0

    repo.actualizar_estado(t1.id, usuario1.id, EstadoEnum.en_progreso, db=db_session)
    repo.actualizar_estado(t2.id, usuario1.id, EstadoEnum.en_progreso, db=db_session)
    repo.actualizar_estado(t3.id, usuario1.id, EstadoEnum.completada, db=db_session)

    assert repo.contar_por_estado(usuario1.id, EstadoEnum.pendiente, db=db_session) == 0
    assert repo.contar_por_estado(usuario1.id, EstadoEnum.en_progreso, db=db_session) == 2
    assert repo.contar_por_estado(usuario1.id, EstadoEnum.completada, db=db_session) == 1

    # Usuario 2 sigue teniendo 1 pendiente
    assert repo.contar_por_estado(usuario2.id, EstadoEnum.pendiente, db=db_session) == 1
    assert repo.contar_por_estado(usuario2.id, EstadoEnum.en_progreso, db=db_session) == 0


def test_listar_tareas_paginacion_y_orden(db_session):
    """Verifica listar_tareas con orden descendente, filtros y paginación."""
    repo = TareasRepository()
    usuario = _crear_usuario(db_session, "list_user@example.com")

    t1 = repo.crear_tarea(datos=TareaCreate(titulo="Tarea 1", prioridad=PrioridadEnum.baja), usuario_id=usuario.id, db=db_session)
    t2 = repo.crear_tarea(datos=TareaCreate(titulo="Tarea 2", prioridad=PrioridadEnum.alta), usuario_id=usuario.id, db=db_session)
    t3 = repo.crear_tarea(datos=TareaCreate(titulo="Tarea 3", prioridad=PrioridadEnum.alta), usuario_id=usuario.id, db=db_session)

    # Orden descendente por id y fecha: [t3, t2, t1]
    todas = repo.listar_tareas(usuario_id=usuario.id, skip=0, limit=10, db=db_session)
    assert [t.id for t in todas] == [t3.id, t2.id, t1.id]

    # Paginación
    pagina1 = repo.listar_tareas(usuario_id=usuario.id, skip=0, limit=2, db=db_session)
    assert [t.id for t in pagina1] == [t3.id, t2.id]

    pagina2 = repo.listar_tareas(usuario_id=usuario.id, skip=2, limit=2, db=db_session)
    assert [t.id for t in pagina2] == [t1.id]

    # Filtro por prioridad
    altas = repo.listar_tareas(usuario_id=usuario.id, prioridad=PrioridadEnum.alta, db=db_session)
    assert len(altas) == 2
    assert all(t.prioridad == PrioridadEnum.alta for t in altas)


