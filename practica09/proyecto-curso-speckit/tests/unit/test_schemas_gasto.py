import pytest
from pydantic import ValidationError
from app.schemas.gasto import GastoCreate, GastoResponse, GastoOut
from app.models.gasto import Gasto

def test_gasto_create_valido():
    g = GastoCreate(descripcion="Almuerzo", monto=15.5, categoria="comida")
    assert g.descripcion == "Almuerzo"
    assert g.monto == 15.5
    assert g.categoria == "comida"

def test_gasto_create_monto_invalido():
    # Monto cero
    with pytest.raises(ValidationError):
        GastoCreate(descripcion="Almuerzo", monto=0.0, categoria="comida")
    # Monto negativo
    with pytest.raises(ValidationError):
        GastoCreate(descripcion="Almuerzo", monto=-10.0, categoria="comida")

def test_gasto_create_descripcion_vacia():
    # Vacia
    with pytest.raises(ValidationError):
        GastoCreate(descripcion="", monto=10.0, categoria="comida")
    # Espacios en blanco
    with pytest.raises(ValidationError):
        GastoCreate(descripcion="   ", monto=10.0, categoria="comida")

def test_gasto_response_serialization():
    orm_gasto = Gasto(id=1, usuario_id=5, descripcion="Café", monto=3.5, categoria="comida")
    resp = GastoResponse.model_validate(orm_gasto)
    assert resp.id == 1
    assert resp.descripcion == "Café"
    assert resp.monto == 3.5
    assert resp.categoria == "comida"
    assert resp.usuario_id == 5
