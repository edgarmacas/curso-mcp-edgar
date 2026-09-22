"""Repositorio de persistencia para tareas."""

from typing import Optional, List, Any
from sqlalchemy.orm import Session
from app.models.tarea import Tarea
from app.schemas.tarea import PrioridadEnum, EstadoEnum, TareaCreate
from app.database import SessionLocal
from app.utils.date_utils import now_utc


class TareasRepository:
    """Operaciones de base de datos para la entidad Tarea."""

    def _resolve_db(self, db: Optional[Session]) -> tuple[Session, bool]:
        if db is not None:
            return db, False
        return SessionLocal(), True

    def crear_tarea(
        self,
        datos: Any,
        usuario_id: int,
        db: Optional[Session] = None,
    ) -> Tarea:
        """Crea y persiste una nueva tarea asociada al usuario autenticado."""
        session, is_local = self._resolve_db(db)
        try:
            titulo = getattr(datos, "titulo", None) or datos.get("titulo")
            descripcion = getattr(datos, "descripcion", None) or (
                datos.get("descripcion") if isinstance(datos, dict) else None
            )
            prioridad = getattr(datos, "prioridad", PrioridadEnum.media)
            if isinstance(datos, dict):
                prioridad = datos.get("prioridad", PrioridadEnum.media)
            fecha_limite = getattr(datos, "fecha_limite", None) or (
                datos.get("fecha_limite") if isinstance(datos, dict) else None
            )

            prio_enum = (
                prioridad if isinstance(prioridad, PrioridadEnum) else PrioridadEnum(prioridad)
            )

            tarea = Tarea(
                usuario_id=usuario_id,
                titulo=titulo,
                descripcion=descripcion,
                prioridad=prio_enum,
                fecha_limite=fecha_limite,
                estado=EstadoEnum.pendiente,
            )
            session.add(tarea)
            session.commit()
            session.refresh(tarea)
            return tarea
        finally:
            if is_local:
                session.close()

    def contar_abiertas_por_prioridad(
        self,
        usuario_id: int,
        prioridad: Any,
        db: Optional[Session] = None,
    ) -> int:
        """Cuenta tareas abiertas (pendiente o en_progreso) por usuario y prioridad."""
        session, is_local = self._resolve_db(db)
        try:
            valor_prioridad = prioridad.value if hasattr(prioridad, "value") else str(prioridad)
            return (
                session.query(Tarea)
                .filter(
                    Tarea.usuario_id == usuario_id,
                    Tarea.prioridad == valor_prioridad,
                    Tarea.estado.in_([EstadoEnum.pendiente, EstadoEnum.en_progreso]),
                )
                .count()
            )
        finally:
            if is_local:
                session.close()

    def contar_por_estado(
        self,
        usuario_id: int,
        estado: Any,
        db: Optional[Session] = None,
    ) -> int:
        """Cuenta tareas de un usuario en un estado específico."""
        session, is_local = self._resolve_db(db)
        try:
            valor_estado = estado.value if hasattr(estado, "value") else str(estado)
            return (
                session.query(Tarea)
                .filter(
                    Tarea.usuario_id == usuario_id,
                    Tarea.estado == valor_estado,
                )
                .count()
            )
        finally:
            if is_local:
                session.close()

    def obtener_por_id(
        self,
        tarea_id: int,
        usuario_id: int,
        db: Optional[Session] = None,
    ) -> Optional[Tarea]:
        """Obtiene una tarea por ID siempre que pertenezca al usuario especificado."""
        session, is_local = self._resolve_db(db)
        try:
            return (
                session.query(Tarea)
                .filter(Tarea.id == tarea_id, Tarea.usuario_id == usuario_id)
                .first()
            )
        finally:
            if is_local:
                session.close()

    def buscar_por_id_global(
        self,
        tarea_id: int,
        db: Optional[Session] = None,
    ) -> Optional[Tarea]:
        """Busca una tarea por ID sin filtrar por usuario (para distinguir 403 de 404)."""
        session, is_local = self._resolve_db(db)
        try:
            return session.query(Tarea).filter(Tarea.id == tarea_id).first()
        finally:
            if is_local:
                session.close()

    def listar_tareas(
        self,
        usuario_id: int,
        skip: int = 0,
        limit: int = 20,
        estado: Optional[Any] = None,
        prioridad: Optional[Any] = None,
        db: Optional[Session] = None,
    ) -> List[Tarea]:
        """Lista tareas del usuario con paginación, filtros y orden descendente."""
        session, is_local = self._resolve_db(db)
        try:
            query = session.query(Tarea).filter(Tarea.usuario_id == usuario_id)
            if estado:
                valor_estado = estado.value if hasattr(estado, "value") else str(estado)
                query = query.filter(Tarea.estado == valor_estado)
            if prioridad:
                valor_prioridad = (
                    prioridad.value if hasattr(prioridad, "value") else str(prioridad)
                )
                query = query.filter(Tarea.prioridad == valor_prioridad)

            return (
                query.order_by(Tarea.creado_en.desc(), Tarea.id.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        finally:
            if is_local:
                session.close()

    def actualizar_estado(
        self,
        tarea_id: int,
        usuario_id: int,
        nuevo_estado: Any,
        db: Optional[Session] = None,
    ) -> Optional[Tarea]:
        """Actualiza el estado de una tarea y persiste los cambios."""
        session, is_local = self._resolve_db(db)
        try:
            tarea = (
                session.query(Tarea)
                .filter(Tarea.id == tarea_id, Tarea.usuario_id == usuario_id)
                .first()
            )
            if not tarea:
                return None

            valor_estado = (
                nuevo_estado if isinstance(nuevo_estado, EstadoEnum) else EstadoEnum(nuevo_estado)
            )
            tarea.estado = valor_estado
            tarea.actualizado_en = now_utc()
            session.commit()
            session.refresh(tarea)
            return tarea
        finally:
            if is_local:
                session.close()

    def eliminar_tarea(
        self,
        tarea_id: int,
        usuario_id: int,
        db: Optional[Session] = None,
    ) -> bool:
        """Elimina una tarea de la base de datos."""
        session, is_local = self._resolve_db(db)
        try:
            tarea = (
                session.query(Tarea)
                .filter(Tarea.id == tarea_id, Tarea.usuario_id == usuario_id)
                .first()
            )
            if not tarea:
                return False
            session.delete(tarea)
            session.commit()
            return True
        finally:
            if is_local:
                session.close()


tareas_repository = TareasRepository()
