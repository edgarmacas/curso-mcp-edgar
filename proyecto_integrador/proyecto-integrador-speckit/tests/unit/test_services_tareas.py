"""Pruebas unitarias para la lógica de negocio de tareas en app/services/tareas_service.py."""

import pytest
from app.schemas.tarea import PrioridadEnum, EstadoEnum, TareaCreate
from app.services.tareas_service import (
    crear_tarea,
    cambiar_estado_tarea,
    listar_tareas,
    obtener_tarea_por_id,
    eliminar_tarea,
    iniciar_tarea_prioritaria,
)
from app.services.exceptions import (
    LimitePrioridadAltaExcedidoError,
    LimiteWIPExcedidoError,
    TransicionEstadoInvalidaError,
    RecursoAjenoError,
    RecursoNoEncontradoError,
)


def test_crear_tarea_hasta_limite_prioridad_alta(fake_tareas_repo):
    """Verifica que se puedan crear hasta 2 tareas de prioridad alta sin error."""
    u_id = 1
    t1 = crear_tarea(
        datos=TareaCreate(titulo="Tarea Alta 1", prioridad=PrioridadEnum.alta),
        usuario_id=u_id,
        repo=fake_tareas_repo,
    )
    t2 = crear_tarea(
        datos=TareaCreate(titulo="Tarea Alta 2", prioridad=PrioridadEnum.alta),
        usuario_id=u_id,
        repo=fake_tareas_repo,
    )

    assert t1["id"] == 1
    assert t2["id"] == 2
    assert fake_tareas_repo.contar_abiertas_por_prioridad(u_id, PrioridadEnum.alta) == 2


def test_crear_tercera_tarea_prioridad_alta_falla(fake_tareas_repo):
    """Verifica que intentar crear una 3ra tarea de prioridad alta lance LimitePrioridadAltaExcedidoError (Error Case 2)."""
    u_id = 1
    crear_tarea(
        datos=TareaCreate(titulo="Tarea Alta 1", prioridad=PrioridadEnum.alta),
        usuario_id=u_id,
        repo=fake_tareas_repo,
    )
    crear_tarea(
        datos=TareaCreate(titulo="Tarea Alta 2", prioridad=PrioridadEnum.alta),
        usuario_id=u_id,
        repo=fake_tareas_repo,
    )

    with pytest.raises(LimitePrioridadAltaExcedidoError) as exc_info:
        crear_tarea(
            datos=TareaCreate(titulo="Tarea Alta 3", prioridad=PrioridadEnum.alta),
            usuario_id=u_id,
            repo=fake_tareas_repo,
        )

    assert "tareas de prioridad alta" in str(exc_info.value)


def test_crear_tarea_prioridad_media_o_baja_con_limite_alta_lleno(fake_tareas_repo):
    """Verifica que tener el límite de prioridad alta lleno no impida crear tareas medias o bajas."""
    u_id = 1
    crear_tarea(
        datos=TareaCreate(titulo="Tarea Alta 1", prioridad=PrioridadEnum.alta),
        usuario_id=u_id,
        repo=fake_tareas_repo,
    )
    crear_tarea(
        datos=TareaCreate(titulo="Tarea Alta 2", prioridad=PrioridadEnum.alta),
        usuario_id=u_id,
        repo=fake_tareas_repo,
    )

    # Crear tarea media
    t_media = crear_tarea(
        datos=TareaCreate(titulo="Tarea Media", prioridad=PrioridadEnum.media),
        usuario_id=u_id,
        repo=fake_tareas_repo,
    )
    assert t_media["prioridad"] == "media"

    # Crear tarea baja
    t_baja = crear_tarea(
        datos=TareaCreate(titulo="Tarea Baja", prioridad=PrioridadEnum.baja),
        usuario_id=u_id,
        repo=fake_tareas_repo,
    )
    assert t_baja["prioridad"] == "baja"


def test_tarea_alta_completada_libera_cupo(fake_tareas_repo):
    """Verifica que si una tarea de prioridad alta se completa, se libera el cupo para crear otra."""
    u_id = 1
    t1 = crear_tarea(
        datos=TareaCreate(titulo="Tarea Alta 1", prioridad=PrioridadEnum.alta),
        usuario_id=u_id,
        repo=fake_tareas_repo,
    )
    crear_tarea(
        datos=TareaCreate(titulo="Tarea Alta 2", prioridad=PrioridadEnum.alta),
        usuario_id=u_id,
        repo=fake_tareas_repo,
    )

    # Completar la primera tarea
    fake_tareas_repo.actualizar_estado(t1["id"], u_id, EstadoEnum.completada)

    # Ahora sí debe permitir crear otra tarea de prioridad alta
    t3 = crear_tarea(
        datos=TareaCreate(titulo="Tarea Alta 3", prioridad=PrioridadEnum.alta),
        usuario_id=u_id,
        repo=fake_tareas_repo,
    )
    assert t3["id"] == 3


def test_aislamiento_limite_prioridad_alta_entre_usuarios(fake_tareas_repo):
    """Verifica que las tareas de prioridad alta de otro usuario no afecten el límite del usuario actual."""
    crear_tarea(
        datos=TareaCreate(titulo="Tarea Alta User 1 - A", prioridad=PrioridadEnum.alta),
        usuario_id=1,
        repo=fake_tareas_repo,
    )
    crear_tarea(
        datos=TareaCreate(titulo="Tarea Alta User 1 - B", prioridad=PrioridadEnum.alta),
        usuario_id=1,
        repo=fake_tareas_repo,
    )

    # Usuario 2 aún no tiene tareas de prioridad alta, debe poder crearla
    t_u2 = crear_tarea(
        datos=TareaCreate(titulo="Tarea Alta User 2 - A", prioridad=PrioridadEnum.alta),
        usuario_id=2,
        repo=fake_tareas_repo,
    )
    assert t_u2["usuario_id"] == 2


def test_transicion_estado_valida_secuencia(fake_tareas_repo):
    """Verifica transiciones válidas: pendiente -> en_progreso -> completada."""
    u_id = 1
    t = crear_tarea(datos=TareaCreate(titulo="Tarea flujo"), usuario_id=u_id, repo=fake_tareas_repo)
    assert t["estado"] == "pendiente"

    t_en_prog = cambiar_estado_tarea(
        tarea_id=t["id"],
        nuevo_estado=EstadoEnum.en_progreso,
        usuario_id=u_id,
        repo=fake_tareas_repo,
    )
    assert t_en_prog["estado"] == "en_progreso"

    t_comp = cambiar_estado_tarea(
        tarea_id=t["id"],
        nuevo_estado=EstadoEnum.completada,
        usuario_id=u_id,
        repo=fake_tareas_repo,
    )
    assert t_comp["estado"] == "completada"


def test_transicion_invalida_pendiente_a_completada_falla(fake_tareas_repo):
    """Verifica que saltar de pendiente a completada lance TransicionEstadoInvalidaError (Error Case 4)."""
    u_id = 1
    t = crear_tarea(datos=TareaCreate(titulo="Tarea salto"), usuario_id=u_id, repo=fake_tareas_repo)

    with pytest.raises(TransicionEstadoInvalidaError):
        cambiar_estado_tarea(
            tarea_id=t["id"],
            nuevo_estado=EstadoEnum.completada,
            usuario_id=u_id,
            repo=fake_tareas_repo,
        )


def test_transicion_invalida_desde_completada_falla(fake_tareas_repo):
    """Verifica que modificar una tarea ya completada lance TransicionEstadoInvalidaError."""
    u_id = 1
    t = crear_tarea(datos=TareaCreate(titulo="Tarea finalizada"), usuario_id=u_id, repo=fake_tareas_repo)
    cambiar_estado_tarea(t["id"], EstadoEnum.en_progreso, u_id, repo=fake_tareas_repo)
    cambiar_estado_tarea(t["id"], EstadoEnum.completada, u_id, repo=fake_tareas_repo)

    with pytest.raises(TransicionEstadoInvalidaError):
        cambiar_estado_tarea(t["id"], EstadoEnum.en_progreso, u_id, repo=fake_tareas_repo)

    with pytest.raises(TransicionEstadoInvalidaError):
        cambiar_estado_tarea(t["id"], EstadoEnum.pendiente, u_id, repo=fake_tareas_repo)


def test_limite_wip_excedido_en_cuarta_tarea_falla(fake_tareas_repo):
    """Verifica que mover una 4ta tarea a en_progreso lance LimiteWIPExcedidoError (Error Case 3)."""
    u_id = 1
    # Crear 4 tareas
    t1 = crear_tarea(datos=TareaCreate(titulo="T1"), usuario_id=u_id, repo=fake_tareas_repo)
    t2 = crear_tarea(datos=TareaCreate(titulo="T2"), usuario_id=u_id, repo=fake_tareas_repo)
    t3 = crear_tarea(datos=TareaCreate(titulo="T3"), usuario_id=u_id, repo=fake_tareas_repo)
    t4 = crear_tarea(datos=TareaCreate(titulo="T4"), usuario_id=u_id, repo=fake_tareas_repo)

    # Mover 3 tareas a en_progreso (Límite WIP = 3)
    cambiar_estado_tarea(t1["id"], EstadoEnum.en_progreso, u_id, repo=fake_tareas_repo)
    cambiar_estado_tarea(t2["id"], EstadoEnum.en_progreso, u_id, repo=fake_tareas_repo)
    cambiar_estado_tarea(t3["id"], EstadoEnum.en_progreso, u_id, repo=fake_tareas_repo)

    # Intentar mover la 4ta tarea a en_progreso -> debe fallar con LimiteWIPExcedidoError
    with pytest.raises(LimiteWIPExcedidoError) as exc_info:
        cambiar_estado_tarea(t4["id"], EstadoEnum.en_progreso, u_id, repo=fake_tareas_repo)

    assert "tareas en progreso" in str(exc_info.value)

    # Si una tarea en_progreso se completa, se libera un cupo WIP
    cambiar_estado_tarea(t1["id"], EstadoEnum.completada, u_id, repo=fake_tareas_repo)
    t4_actualizada = cambiar_estado_tarea(t4["id"], EstadoEnum.en_progreso, u_id, repo=fake_tareas_repo)
    assert t4_actualizada["estado"] == "en_progreso"


def test_cambiar_estado_recurso_no_encontrado_falla(fake_tareas_repo):
    """Verifica que modificar una tarea inexistente lance RecursoNoEncontradoError (Error Case 7)."""
    with pytest.raises(RecursoNoEncontradoError):
        cambiar_estado_tarea(
            tarea_id=99999,
            nuevo_estado=EstadoEnum.en_progreso,
            usuario_id=1,
            repo=fake_tareas_repo,
        )


def test_cambiar_estado_recurso_ajeno_falla(fake_tareas_repo):
    """Verifica que modificar una tarea de otro usuario lance RecursoAjenoError (Error Case 6)."""
    # Usuario 1 crea la tarea
    t = crear_tarea(datos=TareaCreate(titulo="Tarea de user 1"), usuario_id=1, repo=fake_tareas_repo)

    # Usuario 2 intenta modificar el estado
    with pytest.raises(RecursoAjenoError):
        cambiar_estado_tarea(
            tarea_id=t["id"],
            nuevo_estado=EstadoEnum.en_progreso,
            usuario_id=2,
            repo=fake_tareas_repo,
        )


def test_listar_tareas_usuario_aislamiento_y_filtros(fake_tareas_repo):
    """Verifica listar_tareas con filtros, paginación y aislamiento por usuario sin mocks."""
    crear_tarea(datos=TareaCreate(titulo="U1-1", prioridad=PrioridadEnum.alta), usuario_id=1, repo=fake_tareas_repo)
    crear_tarea(datos=TareaCreate(titulo="U1-2", prioridad=PrioridadEnum.baja), usuario_id=1, repo=fake_tareas_repo)
    crear_tarea(datos=TareaCreate(titulo="U2-1", prioridad=PrioridadEnum.alta), usuario_id=2, repo=fake_tareas_repo)

    # Usuario 1 solo ve sus tareas
    u1_tareas = listar_tareas(usuario_id=1, repo=fake_tareas_repo)
    assert len(u1_tareas) == 2
    assert all(t["usuario_id"] == 1 for t in u1_tareas)

    # Filtro por prioridad
    u1_altas = listar_tareas(usuario_id=1, prioridad=PrioridadEnum.alta, repo=fake_tareas_repo)
    assert len(u1_altas) == 1
    assert u1_altas[0]["titulo"] == "U1-1"


def test_obtener_tarea_por_id_exitoso_y_errores(fake_tareas_repo):
    """Verifica obtener_tarea_por_id, 403 en tarea ajena (Error Case 6) y 404 en inexistente (Error Case 7)."""
    t1 = crear_tarea(datos=TareaCreate(titulo="Tarea Privada"), usuario_id=1, repo=fake_tareas_repo)

    # Propietario consulta con éxito
    obtenida = obtener_tarea_por_id(tarea_id=t1["id"], usuario_id=1, repo=fake_tareas_repo)
    assert obtenida["id"] == t1["id"]

    # Usuario ajeno lanza RecursoAjenoError (403)
    with pytest.raises(RecursoAjenoError):
        obtener_tarea_por_id(tarea_id=t1["id"], usuario_id=2, repo=fake_tareas_repo)

    # Tarea inexistente lanza RecursoNoEncontradoError (404)
    with pytest.raises(RecursoNoEncontradoError):
        obtener_tarea_por_id(tarea_id=99999, usuario_id=1, repo=fake_tareas_repo)


def test_eliminar_tarea_exitoso_y_errores(fake_tareas_repo):
    """Verifica eliminar_tarea, 403 en tarea ajena (Error Case 6) y 404 en inexistente (Error Case 7)."""
    t = crear_tarea(datos=TareaCreate(titulo="Tarea a eliminar"), usuario_id=1, repo=fake_tareas_repo)

    # Usuario ajeno lanza RecursoAjenoError (403)
    with pytest.raises(RecursoAjenoError):
        eliminar_tarea(tarea_id=t["id"], usuario_id=2, repo=fake_tareas_repo)

    # Tarea inexistente lanza RecursoNoEncontradoError (404)
    with pytest.raises(RecursoNoEncontradoError):
        eliminar_tarea(tarea_id=99999, usuario_id=1, repo=fake_tareas_repo)

    # Propietario elimina con éxito
    eliminado = eliminar_tarea(tarea_id=t["id"], usuario_id=1, repo=fake_tareas_repo)
    assert eliminado is True
    assert fake_tareas_repo.obtener_por_id(tarea_id=t["id"], usuario_id=1) is None


def test_iniciar_tarea_prioritaria_selecciona_mayor_prioridad(fake_tareas_repo):
    """Verifica que iniciar_tarea_prioritaria seleccione la tarea pendiente con mayor prioridad."""
    u_id = 1
    # Crear tareas con diferentes prioridades (todas pendientes)
    t_baja = crear_tarea(datos=TareaCreate(titulo="Baja", prioridad=PrioridadEnum.baja), usuario_id=u_id, repo=fake_tareas_repo)
    t_alta = crear_tarea(datos=TareaCreate(titulo="Alta", prioridad=PrioridadEnum.alta), usuario_id=u_id, repo=fake_tareas_repo)
    t_media = crear_tarea(datos=TareaCreate(titulo="Media", prioridad=PrioridadEnum.media), usuario_id=u_id, repo=fake_tareas_repo)

    iniciada = iniciar_tarea_prioritaria(usuario_id=u_id, repo=fake_tareas_repo)
    assert iniciada is not None
    assert iniciada["id"] == t_alta["id"]
    assert iniciada["estado"] == "en_progreso"


def test_iniciar_tarea_prioritaria_desempate_por_antiguedad(fake_tareas_repo):
    """Verifica que ante empate en prioridad alta, se seleccione la tarea más antigua."""
    u_id = 1
    t_alta1 = crear_tarea(datos=TareaCreate(titulo="Alta Primera", prioridad=PrioridadEnum.alta), usuario_id=u_id, repo=fake_tareas_repo)
    t_alta2 = crear_tarea(datos=TareaCreate(titulo="Alta Segunda", prioridad=PrioridadEnum.alta), usuario_id=u_id, repo=fake_tareas_repo)

    iniciada = iniciar_tarea_prioritaria(usuario_id=u_id, repo=fake_tareas_repo)
    assert iniciada["id"] == t_alta1["id"]
    assert iniciada["titulo"] == "Alta Primera"


def test_iniciar_tarea_prioritaria_sin_pendientes_retorna_none(fake_tareas_repo):
    """Verifica que si no hay tareas pendientes retorne None."""
    u_id = 1
    assert iniciar_tarea_prioritaria(usuario_id=u_id, repo=fake_tareas_repo) is None


def test_iniciar_tarea_prioritaria_respeta_limite_wip(fake_tareas_repo):
    """Verifica que iniciar_tarea_prioritaria falle con LimiteWIPExcedidoError si ya hay 3 en progreso."""
    u_id = 1
    # Crear y poner 3 en progreso
    for i in range(3):
        t = crear_tarea(datos=TareaCreate(titulo=f"Progreso {i}"), usuario_id=u_id, repo=fake_tareas_repo)
        cambiar_estado_tarea(t["id"], EstadoEnum.en_progreso, u_id, repo=fake_tareas_repo)

    # Crear una 4ta tarea pendiente
    crear_tarea(datos=TareaCreate(titulo="Pendiente"), usuario_id=u_id, repo=fake_tareas_repo)

    # Intentar iniciar tarea prioritaria debe levantar LimiteWIPExcedidoError
    with pytest.raises(LimiteWIPExcedidoError):
        iniciar_tarea_prioritaria(usuario_id=u_id, repo=fake_tareas_repo)




