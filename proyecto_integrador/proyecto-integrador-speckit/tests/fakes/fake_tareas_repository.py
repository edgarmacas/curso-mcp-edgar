"""Repositorio falso en memoria para tareas (DIP, sin unittest.mock)."""

from typing import Optional, List, Dict, Any
from app.utils.date_utils import now_utc


class FakeTareasRepository:
    """Implementación en memoria de operaciones de persistencia para tareas."""

    def __init__(self):
        self._tareas: Dict[int, Dict[str, Any]] = {}
        self._contador_id = 1

    def crear_tarea(
        self,
        datos: Any,
        usuario_id: int,
        db: Any = None,
    ) -> Dict[str, Any]:
        if hasattr(datos, "model_dump"):
            datos_dict = datos.model_dump()
        else:
            datos_dict = dict(datos)

        tarea_id = self._contador_id
        self._contador_id += 1
        ahora = now_utc()

        prioridad_val = datos_dict.get("prioridad", "media")
        if hasattr(prioridad_val, "value"):
            prioridad_val = prioridad_val.value

        estado_val = datos_dict.get("estado", "pendiente")
        if hasattr(estado_val, "value"):
            estado_val = estado_val.value

        tarea = {
            "id": tarea_id,
            "usuario_id": usuario_id,
            "titulo": datos_dict.get("titulo"),
            "descripcion": datos_dict.get("descripcion"),
            "prioridad": prioridad_val,
            "estado": estado_val,
            "fecha_limite": datos_dict.get("fecha_limite"),
            "creado_en": ahora,
            "actualizado_en": ahora,
        }
        self._tareas[tarea_id] = tarea
        return dict(tarea)

    def obtener_por_id(
        self,
        tarea_id: int,
        usuario_id: int,
        db: Any = None,
    ) -> Optional[Dict[str, Any]]:
        tarea = self._tareas.get(tarea_id)
        if tarea and tarea["usuario_id"] == usuario_id:
            return dict(tarea)
        return None

    def buscar_por_id_global(
        self,
        tarea_id: int,
        db: Any = None,
    ) -> Optional[Dict[str, Any]]:
        tarea = self._tareas.get(tarea_id)
        if tarea:
            return dict(tarea)
        return None

    def listar_tareas(
        self,
        usuario_id: int,
        skip: int = 0,
        limit: int = 20,
        estado: Optional[Any] = None,
        prioridad: Optional[Any] = None,
        db: Any = None,
    ) -> List[Dict[str, Any]]:
        tareas = [
            t for t in self._tareas.values()
            if t["usuario_id"] == usuario_id
        ]
        if estado:
            estado_val = estado.value if hasattr(estado, "value") else str(estado)
            tareas = [t for t in tareas if t["estado"] == estado_val]
        if prioridad:
            prio_val = prioridad.value if hasattr(prioridad, "value") else str(prioridad)
            tareas = [t for t in tareas if t["prioridad"] == prio_val]

        # Ordenamiento descendente por creado_en e id
        tareas.sort(key=lambda x: (x["creado_en"], x["id"]), reverse=True)
        return [dict(t) for t in tareas[skip : skip + limit]]

    def contar_abiertas_por_prioridad(
        self,
        usuario_id: int,
        prioridad: Any,
        db: Any = None,
    ) -> int:
        prio_val = prioridad.value if hasattr(prioridad, "value") else str(prioridad)
        return sum(
            1
            for t in self._tareas.values()
            if t["usuario_id"] == usuario_id
            and t["prioridad"] == prio_val
            and t["estado"] in ("pendiente", "en_progreso")
        )

    def contar_por_estado(
        self,
        usuario_id: int,
        estado: Any,
        db: Any = None,
    ) -> int:
        estado_val = estado.value if hasattr(estado, "value") else str(estado)
        return sum(
            1
            for t in self._tareas.values()
            if t["usuario_id"] == usuario_id and t["estado"] == estado_val
        )

    def actualizar_estado(
        self,
        tarea_id: int,
        usuario_id: int,
        nuevo_estado: Any,
        db: Any = None,
    ) -> Optional[Dict[str, Any]]:
        tarea = self._tareas.get(tarea_id)
        if not tarea or tarea["usuario_id"] != usuario_id:
            return None

        val_estado = nuevo_estado.value if hasattr(nuevo_estado, "value") else str(nuevo_estado)
        tarea["estado"] = val_estado
        tarea["actualizado_en"] = now_utc()
        return dict(tarea)

    def eliminar_tarea(
        self,
        tarea_id: int,
        usuario_id: int,
        db: Any = None,
    ) -> bool:
        tarea = self._tareas.get(tarea_id)
        if tarea and tarea["usuario_id"] == usuario_id:
            del self._tareas[tarea_id]
            return True
        return False
