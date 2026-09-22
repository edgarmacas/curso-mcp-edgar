"""Modelo ORM para Tarea."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.schemas.tarea import PrioridadEnum, EstadoEnum
from app.utils.date_utils import now_utc


class Tarea(Base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    prioridad = Column(Enum(PrioridadEnum), default=PrioridadEnum.media, nullable=False)
    estado = Column(Enum(EstadoEnum), default=EstadoEnum.pendiente, nullable=False)
    fecha_limite = Column(DateTime(timezone=True), nullable=True)
    creado_en = Column(DateTime(timezone=True), default=now_utc, nullable=False)
    actualizado_en = Column(
        DateTime(timezone=True),
        default=now_utc,
        onupdate=now_utc,
        nullable=False,
    )

    usuario = relationship("Usuario", back_populates="tareas")
