from pydantic import BaseModel, ConfigDict, field_validator


class GastoCreate(BaseModel):
    descripcion: str
    monto: float
    categoria: str

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("La descripción no puede estar vacía")
        return v

    @field_validator("monto")
    @classmethod
    def validar_monto(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("El monto debe ser mayor a cero")
        return v


class GastoResponse(BaseModel):
    id: int
    descripcion: str
    monto: float
    categoria: str
    usuario_id: int | None = None
    fecha: str | None = None

    model_config = ConfigDict(from_attributes=True)


GastoOut = GastoResponse
