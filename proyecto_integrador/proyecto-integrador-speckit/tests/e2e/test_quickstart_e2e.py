"""Test End-to-End siguiendo los escenarios de quickstart.md."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db, engine as db_engine, SessionLocal as db_SessionLocal
from app.main import app as fastapi_app
from app.mcp.tools import mcp_crear_tarea, mcp_listar_tareas, mcp_iniciar_tarea_prioritaria
from app.repositories.tareas_repository import tareas_repository


@pytest.fixture
def e2e_client(monkeypatch):
    """Cliente de pruebas E2E con base de datos SQLite en memoria aislada compartida por REST y MCP."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    import app.database as database_module
    import app.repositories.tareas_repository as repo_module
    monkeypatch.setattr(database_module, "engine", engine)
    monkeypatch.setattr(database_module, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(repo_module, "SessionLocal", TestingSessionLocal)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db

    with TestClient(fastapi_app) as client:
        yield client, TestingSessionLocal

    fastapi_app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_quickstart_full_flow_scenarios(e2e_client):
    """Ejecuta el flujo completo de quickstart.md de forma integrada."""
    client, SessionLocal = e2e_client

    # -------------------------------------------------------------
    # Escenario 1: Registro e Inicio de Sesión
    # -------------------------------------------------------------
    reg_payload = {"email": "edgar@ejemplo.com", "password": "passwordSeguro123"}
    resp_reg = client.post("/usuarios/", json=reg_payload)
    assert resp_reg.status_code == 201, f"Fallo al registrar usuario: {resp_reg.text}"
    user_data = resp_reg.json()
    assert user_data["email"] == "edgar@ejemplo.com"
    assert "password" not in user_data
    assert "password_hash" not in user_data
    user_id = user_data["id"]

    # Login para obtener JWT
    login_data = {"username": "edgar@ejemplo.com", "password": "passwordSeguro123"}
    resp_login = client.post("/usuarios/token", data=login_data)
    assert resp_login.status_code == 200, f"Fallo al iniciar sesión: {resp_login.text}"
    token_json = resp_login.json()
    assert "access_token" in token_json
    token = token_json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # -------------------------------------------------------------
    # Escenario 2: Límite de Prioridad Alta (Máx 2 abiertas)
    # -------------------------------------------------------------
    # Tarea 1: Alta -> 201
    resp_t1 = client.post(
        "/tareas/",
        headers=headers,
        json={"titulo": "Tarea Crítica 1", "prioridad": "alta"},
    )
    assert resp_t1.status_code == 201
    t1_id = resp_t1.json()["id"]

    # Tarea 2: Alta -> 201
    resp_t2 = client.post(
        "/tareas/",
        headers=headers,
        json={"titulo": "Tarea Crítica 2", "prioridad": "alta"},
    )
    assert resp_t2.status_code == 201
    t2_id = resp_t2.json()["id"]

    # Tarea 3: Alta -> 400 Bad Request (Límite de prioridad alta alcanzado)
    resp_t3_fail = client.post(
        "/tareas/",
        headers=headers,
        json={"titulo": "Tarea Crítica 3", "prioridad": "alta"},
    )
    assert resp_t3_fail.status_code == 400
    assert "prioridad alta" in resp_t3_fail.json()["detail"].lower()

    # Tareas en otras prioridades sí se permiten aunque prioridad alta esté al tope
    resp_t3 = client.post(
        "/tareas/",
        headers=headers,
        json={"titulo": "Tarea Media 3", "prioridad": "media"},
    )
    assert resp_t3.status_code == 201
    t3_id = resp_t3.json()["id"]

    resp_t4 = client.post(
        "/tareas/",
        headers=headers,
        json={"titulo": "Tarea Baja 4", "prioridad": "baja"},
    )
    assert resp_t4.status_code == 201
    t4_id = resp_t4.json()["id"]

    # -------------------------------------------------------------
    # Escenario 3: Transición de Estado y Límite WIP (Máx 3 en progreso)
    # -------------------------------------------------------------
    # Intento de salto inválido: pendiente -> completada (debe fallar con 400)
    resp_invalid_trans = client.patch(
        f"/tareas/{t1_id}/estado",
        headers=headers,
        json={"estado": "completada"},
    )
    assert resp_invalid_trans.status_code == 400
    assert "no se permite" in resp_invalid_trans.json()["detail"].lower() or "transición" in resp_invalid_trans.json()["detail"].lower()

    # Mover 3 tareas a en_progreso (alcanzando el límite WIP de 3)
    for tid in [t1_id, t2_id, t3_id]:
        resp_wip = client.patch(
            f"/tareas/{tid}/estado",
            headers=headers,
            json={"estado": "en_progreso"},
        )
        assert resp_wip.status_code == 200
        assert resp_wip.json()["estado"] == "en_progreso"

    # Intentar mover una 4ta tarea a en_progreso -> 400 (Límite WIP excedido)
    resp_wip_fail = client.patch(
        f"/tareas/{t4_id}/estado",
        headers=headers,
        json={"estado": "en_progreso"},
    )
    assert resp_wip_fail.status_code == 400
    assert "wip" in resp_wip_fail.json()["detail"].lower() or "progreso" in resp_wip_fail.json()["detail"].lower()

    # Completar una tarea para liberar cupo WIP y cupo de prioridad alta
    resp_complete = client.patch(
        f"/tareas/{t1_id}/estado",
        headers=headers,
        json={"estado": "completada"},
    )
    assert resp_complete.status_code == 200
    assert resp_complete.json()["estado"] == "completada"

    # Ahora sí es posible mover t4 a en_progreso
    resp_wip_ok = client.patch(
        f"/tareas/{t4_id}/estado",
        headers=headers,
        json={"estado": "en_progreso"},
    )
    assert resp_wip_ok.status_code == 200

    # Y ahora sí es posible crear otra tarea de prioridad alta (porque t1 se completó)
    resp_t5_alta = client.post(
        "/tareas/",
        headers=headers,
        json={"titulo": "Tarea Crítica 5", "prioridad": "alta"},
    )
    assert resp_t5_alta.status_code == 201
    t5_id = resp_t5_alta.json()["id"]

    # -------------------------------------------------------------
    # Escenario 4: Consultas y Eliminación
    # -------------------------------------------------------------
    # Listar tareas
    resp_list = client.get("/tareas/", headers=headers)
    assert resp_list.status_code == 200
    tareas_list = resp_list.json()
    assert len(tareas_list) >= 4

    # Filtrar por estado
    resp_en_progreso = client.get("/tareas/?estado=en_progreso", headers=headers)
    assert resp_en_progreso.status_code == 200
    for t in resp_en_progreso.json():
        assert t["estado"] == "en_progreso"

    # Eliminar tarea
    resp_del = client.delete(f"/tareas/{t5_id}", headers=headers)
    assert resp_del.status_code == 204

    # Verificar que ya no existe (404)
    resp_get_deleted = client.get(f"/tareas/{t5_id}", headers=headers)
    assert resp_get_deleted.status_code == 404

    # -------------------------------------------------------------
    # Escenario 5: Validación de MCP Tools integradas
    # -------------------------------------------------------------
    # MCP crear tarea
    mcp_res = mcp_crear_tarea(
        titulo="Tarea vía MCP",
        prioridad="media",
        usuario_id=user_id,
    )
    assert mcp_res.get("success") is True, f"Error MCP crear tarea: {mcp_res}"
    assert "tarea" in mcp_res
    assert mcp_res["tarea"]["titulo"] == "Tarea vía MCP"

    # MCP listar tareas
    mcp_lista = mcp_listar_tareas(
        usuario_id=user_id,
    )
    assert mcp_lista.get("success") is True, f"Error MCP listar: {mcp_lista}"
    assert "tareas" in mcp_lista
    assert any(t["titulo"] == "Tarea vía MCP" for t in mcp_lista["tareas"])

    # Completar t2 para liberar WIP antes de iniciar tarea prioritaria
    client.patch(f"/tareas/{t2_id}/estado", headers=headers, json={"estado": "completada"})

    # MCP iniciar tarea prioritaria
    mcp_inicio = mcp_iniciar_tarea_prioritaria(
        usuario_id=user_id,
    )
    assert mcp_inicio.get("success") is True, f"Error MCP iniciar tarea prioritaria: {mcp_inicio}"
    assert "tarea" in mcp_inicio
    assert mcp_inicio["tarea"]["titulo"] == "Tarea vía MCP"
    assert mcp_inicio["tarea"]["estado"] == "en_progreso"
