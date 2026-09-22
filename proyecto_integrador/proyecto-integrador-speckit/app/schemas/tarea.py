"""Esquemas y Enums para Tareas."""

import enum
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator


class PrioridadEnum(str, enum.Enum):
    baja = "baja"
    media = "media"
    alta = "alta"


class EstadoEnum(str, enum.Enum):
    pendiente = "pendiente"
    en_progreso = "en_progreso"
    completada = "completada"


class TareaCreate(BaseModel):
    """Esquema para la creación de una nueva tarea."""
    titulo: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    prioridad: PrioridadEnum = PrioridadEnum.media
    fecha_limite: Optional[datetime] = None

    @field_validator("titulo", mode="before")
    @classmethod
    def strip_and_validate_titulo(cls, v: Any) -> Any:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("El título no puede estar vacío ni contener solo espacios en blanco")
        return v


class TareaUpdateEstado(BaseModel):
    """Esquema para la actualización de estado de una tarea."""
    estado: EstadoEnum


class TareaOut(BaseModel):
    """Esquema de salida para una tarea."""
    id: int
    usuario_id: int
    titulo: str
    descripcion: Optional[str] = None
    prioridad: PrioridadEnum
    estado: EstadoEnum
    fecha_limite: Optional[datetime] = None
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)
