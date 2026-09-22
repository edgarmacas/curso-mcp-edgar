"""Servicio de lógica de negocio para la gestión de tareas personales."""

from typing import Any
from app.schemas.tarea import PrioridadEnum, EstadoEnum, TareaCreate
from app.repositories.tareas_repository import tareas_repository
from app.services.exceptions import (
    LimitePrioridadAltaExcedidoError,
    LimiteWIPExcedidoError,
    TransicionEstadoInvalidaError,
    RecursoAjenoError,
    RecursoNoEncontradoError,
)

LIMITE_TAREAS_PRIORIDAD_ALTA = 2
LIMITE_WIP = 3

TRANSICIONES_VALIDAS = {
    EstadoEnum.pendiente.value: [EstadoEnum.en_progreso.value],
    EstadoEnum.en_progreso.value: [EstadoEnum.completada.value],
    EstadoEnum.completada.value: [],
}


def crear_tarea(
    datos: TareaCreate,
    usuario_id: int,
    db: Any = None,
    repo: Any = tareas_repository,
) -> Any:
    """Crea una tarea validando que el límite de 2 tareas de prioridad alta abiertas no se exceda.

    Cumple con el Artículo I.2 (sin imports de SQLAlchemy/Session) y Artículo II.3 (DIP).
    """
    prioridad_val = (
        datos.prioridad.value
        if isinstance(datos.prioridad, PrioridadEnum)
        else str(datos.prioridad)
    )

    if prioridad_val == PrioridadEnum.alta.value:
        abiertas_alta = repo.contar_abiertas_por_prioridad(
            usuario_id=usuario_id,
            prioridad=PrioridadEnum.alta,
            db=db,
        )
        if abiertas_alta >= LIMITE_TAREAS_PRIORIDAD_ALTA:
            raise LimitePrioridadAltaExcedidoError(
                f"No es posible crear más de {LIMITE_TAREAS_PRIORIDAD_ALTA} tareas de prioridad alta abiertas simultáneamente."
            )

    return repo.crear_tarea(datos=datos, usuario_id=usuario_id, db=db)


def cambiar_estado_tarea(
    tarea_id: int,
    nuevo_estado: EstadoEnum | str,
    usuario_id: int,
    db: Any = None,
    repo: Any = tareas_repository,
) -> Any:
    """Cambia el estado de una tarea aplicando validaciones de pertenencia, máquina de estados y límite WIP."""
    # 1. Verificar existencia global y pertenencia (Error Case 6 y 7)
    tarea_global = repo.buscar_por_id_global(tarea_id=tarea_id, db=db)
    if not tarea_global:
        raise RecursoNoEncontradoError(f"Tarea con ID {tarea_id} no encontrada.")

    owner_id = getattr(tarea_global, "usuario_id", None) or (
        tarea_global.get("usuario_id") if isinstance(tarea_global, dict) else None
    )
    if owner_id != usuario_id:
        raise RecursoAjenoError("No tiene permiso para acceder a este recurso.")

    # 2. Validar transición de estado (Error Case 4)
    estado_actual = getattr(tarea_global, "estado", None) or (
        tarea_global.get("estado") if isinstance(tarea_global, dict) else None
    )
    estado_actual_val = (
        estado_actual.value if hasattr(estado_actual, "value") else str(estado_actual)
    )
    nuevo_estado_val = (
        nuevo_estado.value if hasattr(nuevo_estado, "value") else str(nuevo_estado)
    )

    transiciones_permitidas = TRANSICIONES_VALIDAS.get(estado_actual_val, [])
    if nuevo_estado_val not in transiciones_permitidas:
        raise TransicionEstadoInvalidaError(
            f"No se permite pasar de '{estado_actual_val}' a '{nuevo_estado_val}'."
        )

    # 3. Validar límite WIP si pasa a 'en_progreso' (Error Case 3)
    if nuevo_estado_val == EstadoEnum.en_progreso.value:
        en_progreso_count = repo.contar_por_estado(
            usuario_id=usuario_id,
            estado=EstadoEnum.en_progreso,
            db=db,
        )
        if en_progreso_count >= LIMITE_WIP:
            raise LimiteWIPExcedidoError(
                f"No se pueden tener más de {LIMITE_WIP} tareas en progreso simultáneamente."
            )

    return repo.actualizar_estado(
        tarea_id=tarea_id,
        usuario_id=usuario_id,
        nuevo_estado=nuevo_estado,
        db=db,
    )


def listar_tareas(
    usuario_id: int,
    skip: int = 0,
    limit: int = 20,
    estado: Any = None,
    prioridad: Any = None,
    db: Any = None,
    repo: Any = tareas_repository,
) -> Any:
    """Lista tareas pertenecientes exclusivamente al usuario autenticado con filtros y paginación."""
    return repo.listar_tareas(
        usuario_id=usuario_id,
        skip=skip,
        limit=limit,
        estado=estado,
        prioridad=prioridad,
        db=db,
    )


def obtener_tarea_por_id(
    tarea_id: int,
    usuario_id: int,
    db: Any = None,
    repo: Any = tareas_repository,
) -> Any:
    """Obtiene una tarea por su ID validando existencia y pertenencia estricta."""
    tarea_global = repo.buscar_por_id_global(tarea_id=tarea_id, db=db)
    if not tarea_global:
        raise RecursoNoEncontradoError(f"Tarea con ID {tarea_id} no encontrada.")

    owner_id = getattr(tarea_global, "usuario_id", None) or (
        tarea_global.get("usuario_id") if isinstance(tarea_global, dict) else None
    )
    if owner_id != usuario_id:
        raise RecursoAjenoError("No tiene permiso para acceder a este recurso.")

    return repo.obtener_por_id(tarea_id=tarea_id, usuario_id=usuario_id, db=db)


def eliminar_tarea(
    tarea_id: int,
    usuario_id: int,
    db: Any = None,
    repo: Any = tareas_repository,
) -> bool:
    """Elimina una tarea verificando existencia global y pertenencia estricta al usuario autenticado."""
    tarea_global = repo.buscar_por_id_global(tarea_id=tarea_id, db=db)
    if not tarea_global:
        raise RecursoNoEncontradoError(f"Tarea con ID {tarea_id} no encontrada.")

    owner_id = getattr(tarea_global, "usuario_id", None) or (
        tarea_global.get("usuario_id") if isinstance(tarea_global, dict) else None
    )
    if owner_id != usuario_id:
        raise RecursoAjenoError("No tiene permiso para acceder a este recurso.")

    return repo.eliminar_tarea(tarea_id=tarea_id, usuario_id=usuario_id, db=db)


PESO_PRIORIDAD = {
    PrioridadEnum.alta.value: 3,
    PrioridadEnum.media.value: 2,
    PrioridadEnum.baja.value: 1,
}


def iniciar_tarea_prioritaria(
    usuario_id: int,
    db: Any = None,
    repo: Any = tareas_repository,
) -> Any:
    """Busca la tarea en estado 'pendiente' con mayor prioridad del usuario y la transiciona a 'en_progreso'.

    En caso de empate en prioridad, selecciona la tarea más antigua (menor fecha de creación / menor id).
    Retorna None si no hay tareas pendientes.
    """
    tareas_pendientes = repo.listar_tareas(
        usuario_id=usuario_id,
        estado=EstadoEnum.pendiente,
        limit=1000,
        db=db,
    )
    if not tareas_pendientes:
        return None

    def criterio(t: Any) -> tuple[int, Any, int]:
        prio = getattr(t, "prioridad", None) or (
            t.get("prioridad") if isinstance(t, dict) else "media"
        )
        prio_val = prio.value if hasattr(prio, "value") else str(prio)
        peso = PESO_PRIORIDAD.get(prio_val, 0)

        creado = getattr(t, "creado_en", None) or (
            t.get("creado_en") if isinstance(t, dict) else ""
        )
        tid = getattr(t, "id", None) or (t.get("id") if isinstance(t, dict) else 0)
        # Mayor prioridad primero (-peso), más antigua primero (creado, tid)
        return (-peso, creado, tid)

    tareas_ordenadas = sorted(tareas_pendientes, key=criterio)
    candidata = tareas_ordenadas[0]
    candidata_id = getattr(candidata, "id", None) or (
        candidata.get("id") if isinstance(candidata, dict) else 0
    )

    return cambiar_estado_tarea(
        tarea_id=candidata_id,
        nuevo_estado=EstadoEnum.en_progreso,
        usuario_id=usuario_id,
        db=db,
        repo=repo,
    )



