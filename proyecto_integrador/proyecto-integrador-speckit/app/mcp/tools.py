"""Herramientas del protocolo MCP conforme al Artículo VI de la Constitución."""

from typing import Optional, Any, Callable
from app.schemas.tarea import PrioridadEnum, EstadoEnum, TareaCreate
from app.services import tareas_service


def mcp_crear_tarea(
    titulo: str,
    prioridad: str,
    descripcion: Optional[str] = None,
    usuario_id: int = 1,
    repo: Any = None,
) -> dict:
    """Crea una tarea personal validando el límite de 2 tareas de prioridad alta abiertas."""
    try:
        datos = TareaCreate(
            titulo=titulo,
            prioridad=prioridad,
            descripcion=descripcion,
        )
        kwargs = {"repo": repo} if repo else {}
        tarea = tareas_service.crear_tarea(datos=datos, usuario_id=usuario_id, **kwargs)

        prio = getattr(tarea, "prioridad", None) or (
            tarea.get("prioridad") if isinstance(tarea, dict) else "media"
        )
        prio_val = prio.value if hasattr(prio, "value") else str(prio)

        estado = getattr(tarea, "estado", None) or (
            tarea.get("estado") if isinstance(tarea, dict) else "pendiente"
        )
        estado_val = estado.value if hasattr(estado, "value") else str(estado)

        return {
            "success": True,
            "tarea": {
                "id": getattr(tarea, "id", None) or tarea.get("id"),
                "titulo": getattr(tarea, "titulo", None) or tarea.get("titulo"),
                "prioridad": prio_val,
                "estado": estado_val,
                "descripcion": getattr(tarea, "descripcion", None)
                or (tarea.get("descripcion") if isinstance(tarea, dict) else None),
                "creado_en": str(
                    getattr(tarea, "creado_en", None)
                    or (tarea.get("creado_en") if isinstance(tarea, dict) else "")
                ),
            },
        }
    except Exception as e:
        return {"error": f"{e.__class__.__name__}: {str(e)}"}


def mcp_listar_tareas(
    usuario_id: int = 1,
    skip: int = 0,
    limit: int = 20,
    estado: Optional[str] = None,
    repo: Any = None,
) -> dict:
    """Lista las tareas personales del usuario autenticado ordenadas por fecha descendente."""
    try:
        kwargs = {"repo": repo} if repo else {}
        tareas = tareas_service.listar_tareas(
            usuario_id=usuario_id,
            skip=skip,
            limit=limit,
            estado=estado,
            **kwargs,
        )

        resultado = []
        for t in tareas:
            prio = getattr(t, "prioridad", None) or (
                t.get("prioridad") if isinstance(t, dict) else "media"
            )
            prio_val = prio.value if hasattr(prio, "value") else str(prio)

            est = getattr(t, "estado", None) or (
                t.get("estado") if isinstance(t, dict) else "pendiente"
            )
            est_val = est.value if hasattr(est, "value") else str(est)

            resultado.append(
                {
                    "id": getattr(t, "id", None) or t.get("id"),
                    "titulo": getattr(t, "titulo", None) or t.get("titulo"),
                    "prioridad": prio_val,
                    "estado": est_val,
                    "descripcion": getattr(t, "descripcion", None)
                    or (t.get("descripcion") if isinstance(t, dict) else None),
                    "creado_en": str(
                        getattr(t, "creado_en", None)
                        or (t.get("creado_en") if isinstance(t, dict) else "")
                    ),
                }
            )

        return {
            "success": True,
            "total": len(resultado),
            "tareas": resultado,
        }
    except Exception as e:
        return {"error": f"{e.__class__.__name__}: {str(e)}"}


def mcp_iniciar_tarea_prioritaria(
    usuario_id: int = 1,
    repo: Any = None,
) -> dict:
    """Busca la tarea pendiente de mayor prioridad y la transiciona a en_progreso respetando límite WIP."""
    try:
        kwargs = {"repo": repo} if repo else {}
        tarea = tareas_service.iniciar_tarea_prioritaria(usuario_id=usuario_id, **kwargs)
        if not tarea:
            return {
                "success": False,
                "mensaje": "No hay tareas pendientes disponibles para iniciar",
            }

        prio = getattr(tarea, "prioridad", None) or (
            tarea.get("prioridad") if isinstance(tarea, dict) else "media"
        )
        prio_val = prio.value if hasattr(prio, "value") else str(prio)

        estado = getattr(tarea, "estado", None) or (
            tarea.get("estado") if isinstance(tarea, dict) else "en_progreso"
        )
        estado_val = estado.value if hasattr(estado, "value") else str(estado)

        return {
            "success": True,
            "mensaje": "Tarea iniciada correctamente",
            "tarea": {
                "id": getattr(tarea, "id", None) or tarea.get("id"),
                "titulo": getattr(tarea, "titulo", None) or tarea.get("titulo"),
                "prioridad": prio_val,
                "estado": estado_val,
                "actualizado_en": str(
                    getattr(tarea, "actualizado_en", None)
                    or (tarea.get("actualizado_en") if isinstance(tarea, dict) else "")
                ),
            },
        }
    except Exception as e:
        return {"error": f"{e.__class__.__name__}: {str(e)}"}


def register_tools(mcp_server: Any, get_user_id_fn: Callable[[], int]):
    """Registra las herramientas oficiales en la instancia MCPServer dada."""

    @mcp_server.tool(
        name="crear_tarea",
        description="Crea una nueva tarea personal validando el límite de un máximo de 2 tareas de prioridad alta abiertas simultáneamente.",
    )
    def crear_tarea(
        titulo: str,
        prioridad: str,
        descripcion: Optional[str] = None,
    ) -> dict:
        uid = get_user_id_fn()
        return mcp_crear_tarea(
            titulo=titulo, prioridad=prioridad, descripcion=descripcion, usuario_id=uid
        )

    @mcp_server.tool(
        name="listar_tareas",
        description="Lista las tareas personales del usuario autenticado ordenadas de forma descendente por fecha de creación, con paginación y filtro opcional por estado.",
    )
    def listar_tareas(
        skip: int = 0,
        limit: int = 20,
        estado: Optional[str] = None,
    ) -> dict:
        uid = get_user_id_fn()
        return mcp_listar_tareas(
            usuario_id=uid, skip=skip, limit=limit, estado=estado
        )

    @mcp_server.tool(
        name="iniciar_tarea_prioritaria",
        description="Busca la tarea en estado 'pendiente' con mayor prioridad ('alta' > 'media' > 'baja') del usuario y la transiciona a 'en_progreso', validando que no se exceda el límite WIP de 3 tareas en progreso.",
    )
    def iniciar_tarea_prioritaria() -> dict:
        uid = get_user_id_fn()
        return mcp_iniciar_tarea_prioritaria(usuario_id=uid)
