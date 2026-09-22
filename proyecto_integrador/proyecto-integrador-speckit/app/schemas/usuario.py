"""DTOs y esquemas Pydantic para Usuario."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Contraseña de mínimo 8 caracteres")


class UsuarioOut(BaseModel):
    id: int
    email: EmailStr
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)
