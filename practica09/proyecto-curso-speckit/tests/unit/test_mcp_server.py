import pytest
from app.mcp.server import registrar_gasto, listar_gastos, mcp
from app.database import SessionLocal, Base, engine


@pytest.fixture(autouse=True)
def setup_db(db_session):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from app.models.gasto import Gasto
        from app.models.usuario import Usuario
        db.query(Gasto).delete()
        db.query(Usuario).delete()
        db.commit()
    finally:
        db.close()
    yield


def test_mcp_registrar_gasto_exito():
    res = registrar_gasto("Café matutino", 5.50, "comida")
    assert "error" not in res
    assert res["descripcion"] == "Café matutino"
    assert res["monto"] == 5.50
    assert res["categoria"] == "comida"


def test_mcp_registrar_gasto_categoria_invalida_retorna_error_estructurado():
    res = registrar_gasto("Nave", 100.0, "categoria_inexistente")
    assert "error" in res
    assert "no es una categoría válida" in res["error"]


def test_mcp_registrar_gasto_monto_invalido_retorna_error_estructurado():
    res = registrar_gasto("Negativo", -10.0, "comida")
    assert "error" in res
    assert "mayor a cero" in res["error"]


def test_mcp_registrar_gasto_limite_excedido_retorna_error_estructurado():
    # Límite es 500. Intentamos registrar 501
    res = registrar_gasto("Super comida", 501.0, "comida")
    assert "error" in res
    assert "supera el límite de 500.0" in res["error"]


def test_mcp_listar_gastos_exito():
    registrar_gasto("Café matutino", 5.50, "comida")
    gastos = listar_gastos(skip=0, limit=10)
    assert isinstance(gastos, list)
    assert len(gastos) >= 1
    assert any(g["descripcion"] == "Café matutino" for g in gastos)


def test_mcp_listar_gastos_paginacion_invalida():
    res_skip = listar_gastos(skip=-1, limit=10)
    assert "error" in res_skip
    assert "Parámetros de paginación inválidos" in res_skip["error"]

    res_limit = listar_gastos(skip=0, limit=0)
    assert "error" in res_limit
    assert "Parámetros de paginación inválidos" in res_limit["error"]
