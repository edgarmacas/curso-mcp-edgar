import pytest
from app.repositories import gastos as gastos_repo
from app.repositories import usuarios as usuarios_repo

def test_guardar_y_total_por_categoria(db_session):
    u1 = usuarios_repo.guardar(db_session, "user1@test.com", "hash")
    u2 = usuarios_repo.guardar(db_session, "user2@test.com", "hash")

    # Guardar gastos para u1
    g1 = gastos_repo.guardar(db_session, u1.id, "Almuerzo", 50.0, "comida")
    assert isinstance(g1, dict)
    assert g1["descripcion"] == "Almuerzo"
    assert g1["monto"] == 50.0

    g2 = gastos_repo.guardar(db_session, u1.id, "Cena", 30.0, "comida")
    assert g2["monto"] == 30.0

    # Guardar gasto de otra categoría para u1
    gastos_repo.guardar(db_session, u1.id, "Metro", 10.0, "transporte")

    # Guardar gasto en comida para u2
    gastos_repo.guardar(db_session, u2.id, "Comida u2", 100.0, "comida")

    # Verificar totales aislados por usuario y categoría
    assert gastos_repo.total_por_categoria(db_session, u1.id, "comida") == 80.0
    assert gastos_repo.total_por_categoria(db_session, u1.id, "transporte") == 10.0
    assert gastos_repo.total_por_categoria(db_session, u1.id, "entretenimiento") == 0.0
    assert gastos_repo.total_por_categoria(db_session, u2.id, "comida") == 100.0

def test_listar_gastos_repo(db_session):
    u = usuarios_repo.guardar(db_session, "listar@test.com", "hash")
    for i in range(5):
        gastos_repo.guardar(db_session, u.id, f"Gasto {i}", 10.0 + i, "otros")

    lista = gastos_repo.listar(db_session, u.id, skip=0, limit=3)
    assert isinstance(lista, list)
    assert len(lista) == 3
    assert all(isinstance(x, dict) for x in lista)
    # Verificar orden descendente (los más recientes primero)
    assert lista[0]["descripcion"] == "Gasto 4"
    assert lista[1]["descripcion"] == "Gasto 3"
    assert lista[2]["descripcion"] == "Gasto 2"

    # Segunda página con skip=3
    lista_pag2 = gastos_repo.listar(db_session, u.id, skip=3, limit=3)
    assert len(lista_pag2) == 2
    assert lista_pag2[0]["descripcion"] == "Gasto 1"
    assert lista_pag2[1]["descripcion"] == "Gasto 0"


def test_listar_gastos_aislamiento_usuario(db_session):
    u1 = usuarios_repo.guardar(db_session, "u1@test.com", "hash")
    u2 = usuarios_repo.guardar(db_session, "u2@test.com", "hash")

    gastos_repo.guardar(db_session, u1.id, "Gasto u1", 25.0, "comida")
    gastos_repo.guardar(db_session, u2.id, "Gasto u2", 35.0, "transporte")

    gastos_u1 = gastos_repo.listar(db_session, u1.id)
    assert len(gastos_u1) == 1
    assert gastos_u1[0]["descripcion"] == "Gasto u1"

    gastos_u2 = gastos_repo.listar(db_session, u2.id)
    assert len(gastos_u2) == 1
    assert gastos_u2[0]["descripcion"] == "Gasto u2"

    gastos_vacio = gastos_repo.listar(db_session, usuario_id=9999)
    assert gastos_vacio == []
