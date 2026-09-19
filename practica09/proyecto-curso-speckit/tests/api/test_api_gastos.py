import pytest
from app.main import app
from app.dependencies import get_current_user, get_gastos_repo
from app.models.usuario import Usuario
from tests.test_gastos import RepositorioFalso

USUARIO_TEST = Usuario(id=1, email="test@ejemplo.com", hashed_password="fake")


@pytest.fixture(autouse=True)
def override_user():
    app.dependency_overrides[get_current_user] = lambda: USUARIO_TEST
    yield
    app.dependency_overrides.clear()


def test_api_crear_gasto_exito(client):
    app.dependency_overrides[get_gastos_repo] = lambda: RepositorioFalso()

    response = client.post(
        "/gastos/",
        json={"descripcion": "Supermercado", "monto": 45.0, "categoria": "comida"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["descripcion"] == "Supermercado"
    assert data["monto"] == 45.0
    assert data["categoria"] == "comida"


def test_api_crear_gasto_monto_invalido_422(client):
    # Error Case 1: Monto negativo o cero
    response = client.post(
        "/gastos/",
        json={"descripcion": "Invalido", "monto": -10.0, "categoria": "comida"},
    )
    assert response.status_code == 422

    response_cero = client.post(
        "/gastos/",
        json={"descripcion": "Cero", "monto": 0.0, "categoria": "comida"},
    )
    assert response_cero.status_code == 422


def test_api_crear_gasto_categoria_invalida_400(client):
    # Error Case 2: Categoría inexistente -> 400
    app.dependency_overrides[get_gastos_repo] = lambda: RepositorioFalso()

    response = client.post(
        "/gastos/",
        json={"descripcion": "Cine", "monto": 25.0, "categoria": "viajes_espaciales"},
    )
    assert response.status_code == 400
    assert "no es una categoría válida" in response.json()["detail"]


def test_api_crear_gasto_limite_excedido_400(client):
    # Error Case 3: Límite de 500 excedido -> 400
    repo = RepositorioFalso(total_inicial_por_categoria=480.0)
    app.dependency_overrides[get_gastos_repo] = lambda: repo

    response = client.post(
        "/gastos/",
        json={"descripcion": "Cena muy cara", "monto": 30.0, "categoria": "comida"},
    )
    assert response.status_code == 400
    assert "supera el límite de 500.0" in response.json()["detail"]


def test_api_listar_gastos_exito(client):
    repo = RepositorioFalso()
    repo.guardar(None, USUARIO_TEST.id, "Metro", 10.0, "transporte")
    repo.guardar(None, USUARIO_TEST.id, "Almuerzo", 20.0, "comida")
    app.dependency_overrides[get_gastos_repo] = lambda: repo

    response = client.get("/gastos/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["descripcion"] == "Metro"
    assert data[1]["descripcion"] == "Almuerzo"


def test_api_listar_gastos_paginacion(client):
    repo = RepositorioFalso()
    for i in range(10):
        repo.guardar(None, USUARIO_TEST.id, f"Gasto {i}", 5.0, "otros")
    app.dependency_overrides[get_gastos_repo] = lambda: repo

    response = client.get("/gastos/?skip=3&limit=4")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    assert data[0]["descripcion"] == "Gasto 3"
    assert data[3]["descripcion"] == "Gasto 6"


def test_api_listar_gastos_skip_negativo_422(client):
    app.dependency_overrides[get_gastos_repo] = lambda: RepositorioFalso()
    response = client.get("/gastos/?skip=-1")
    assert response.status_code == 422


def test_api_listar_gastos_limit_invalido_422(client):
    app.dependency_overrides[get_gastos_repo] = lambda: RepositorioFalso()
    response_cero = client.get("/gastos/?limit=0")
    assert response_cero.status_code == 422

    response_exceso = client.get("/gastos/?limit=101")
    assert response_exceso.status_code == 422
