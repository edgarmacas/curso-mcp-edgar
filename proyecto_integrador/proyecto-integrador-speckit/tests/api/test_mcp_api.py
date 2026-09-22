"""Pruebas de integración API para el punto de entrada FastAPI, manejador de errores 500 y servidor MCP."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.mcp.tools import mcp_crear_tarea, mcp_listar_tareas, mcp_iniciar_tarea_prioritaria
from app.models.usuario import Usuario
from app.services.auth_service import hash_password


@pytest.fixture
def test_client(db_session):
    """Cliente de prueba apuntando a app.main con base de datos en memoria."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client
    app.dependency_overrides.clear()


def test_health_check(test_client):
    """Verifica que el endpoint /health responda HTTP 200 con status ok."""
    res = test_client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_global_exception_handler_returns_500(test_client):
    """Verifica que excepciones no controladas retornen HTTP 500 con formato seguro (Artículo IV.5)."""

    # Definir una ruta temporal que levante una excepción no controlada
    @app.get("/test-error-500")
    def provocar_error_interno():
        raise RuntimeError("Fallo catastrófico imprevisto en subsistema")

    res = test_client.get("/test-error-500")
    assert res.status_code == 500
    assert res.json() == {"detail": "Error interno del servidor"}


def test_mcp_integration_flow(db_session):
    """Verifica el flujo integral agéntico MCP respetando los contratos y límites de capacidad."""
    # 1. Crear usuario de prueba
    usuario = Usuario(
        email="agente_mcp@ejemplo.com",
        password_hash=hash_password("AgentPass123!"),
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    uid = usuario.id

    # 2. Crear 2 tareas de prioridad alta vía tool MCP
    r1 = mcp_crear_tarea(titulo="Alta 1", prioridad="alta", usuario_id=uid)
    assert r1.get("success") is True

    r2 = mcp_crear_tarea(titulo="Alta 2", prioridad="alta", usuario_id=uid)
    assert r2.get("success") is True

    # 3. Intentar crear 3ra tarea alta -> retorna error estructurado sin romper sesión
    r3 = mcp_crear_tarea(titulo="Alta 3", prioridad="alta", usuario_id=uid)
    assert "error" in r3
    assert "LimitePrioridadAltaExcedidoError" in r3["error"]

    # 4. Crear tareas media y baja
    r_media = mcp_crear_tarea(titulo="Media 1", prioridad="media", usuario_id=uid)
    assert r_media.get("success") is True

    r_baja = mcp_crear_tarea(titulo="Baja 1", prioridad="baja", usuario_id=uid)
    assert r_baja.get("success") is True

    # 5. Listar tareas vía tool MCP
    list_res = mcp_listar_tareas(usuario_id=uid)
    assert list_res.get("success") is True
    assert list_res["total"] == 4

    # 6. Iniciar tarea prioritaria -> debe seleccionar la tarea de prioridad alta más antigua
    inicia_res = mcp_iniciar_tarea_prioritaria(usuario_id=uid)
    assert inicia_res.get("success") is True
    assert inicia_res["tarea"]["prioridad"] == "alta"
    assert inicia_res["tarea"]["estado"] == "en_progreso"
    assert inicia_res["tarea"]["id"] == r1["tarea"]["id"]
