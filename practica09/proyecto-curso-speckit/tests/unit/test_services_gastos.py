import pytest
from app.services import gastos as gastos_service
from tests.test_gastos import RepositorioFalso


def test_listar_gastos_servicio_vacio():
    repo = RepositorioFalso()
    gastos = gastos_service.listar_gastos(None, 1, repo=repo)
    assert gastos == []


def test_listar_gastos_servicio_con_elementos():
    repo = RepositorioFalso()
    gastos_service.registrar_gasto(None, 1, "Gasto 1", 10.0, "comida", repo=repo)
    gastos_service.registrar_gasto(None, 1, "Gasto 2", 20.0, "transporte", repo=repo)
    gastos_service.registrar_gasto(None, 1, "Gasto 3", 30.0, "otros", repo=repo)

    gastos = gastos_service.listar_gastos(None, 1, skip=0, limit=20, repo=repo)
    assert len(gastos) == 3
    assert gastos[0]["descripcion"] == "Gasto 1"
    assert gastos[1]["descripcion"] == "Gasto 2"
    assert gastos[2]["descripcion"] == "Gasto 3"


def test_listar_gastos_servicio_paginacion():
    repo = RepositorioFalso()
    for i in range(10):
        gastos_service.registrar_gasto(None, 1, f"Item {i}", 5.0, "otros", repo=repo)

    # Primera página de 4
    pag1 = gastos_service.listar_gastos(None, 1, skip=0, limit=4, repo=repo)
    assert len(pag1) == 4
    assert pag1[0]["descripcion"] == "Item 0"
    assert pag1[3]["descripcion"] == "Item 3"

    # Segunda página de 4 con skip=4
    pag2 = gastos_service.listar_gastos(None, 1, skip=4, limit=4, repo=repo)
    assert len(pag2) == 4
    assert pag2[0]["descripcion"] == "Item 4"
    assert pag2[3]["descripcion"] == "Item 7"


def test_service_no_importa_sqlalchemy():
    import sys
    import app.services.gastos as gs
    import inspect

    source = inspect.getsource(gs)
    assert "sqlalchemy" not in source.lower()
    assert "session" not in source.lower()
