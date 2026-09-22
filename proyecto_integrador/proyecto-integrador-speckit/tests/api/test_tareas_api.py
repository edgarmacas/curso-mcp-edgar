"""Pruebas de integración API para los endpoints de tareas en /tareas/."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers.usuarios import router as usuarios_router
from app.routers.tareas import router as tareas_router
from app.database import get_db
from app.services.auth_service import create_access_token, hash_password
from app.models.usuario import Usuario


@pytest.fixture
def client(db_session):
    """Cliente de prueba con base de datos en memoria y routers de usuarios y tareas montados."""
    app = FastAPI()
    app.include_router(usuarios_router)
    app.include_router(tareas_router)
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client


def _crear_token_usuario(db_session, email="api_user@example.com") -> tuple[str, Usuario]:
    usuario = Usuario(
        email=email,
        password_hash=hash_password("Password123!"),
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    token = create_access_token(data={"sub": email})
    return token, usuario


def test_crear_tarea_sin_autenticacion_retorna_401(client):
    """Verifica que invocar POST /tareas/ sin cabecera Authorization retorne HTTP 401 (Error Case 5)."""
    response = client.post("/tareas/", json={"titulo": "Tarea sin auth"})
    assert response.status_code == 401


def test_crear_tarea_exitosa(client, db_session):
    """Verifica la creación exitosa de una tarea (HTTP 201)."""
    token, usuario = _crear_token_usuario(db_session, "user_ok@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "titulo": "Preparar informe trimestral",
        "descripcion": "Incluir métricas y proyecciones",
        "prioridad": "alta",
    }
    response = client.post("/tareas/", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["usuario_id"] == usuario.id
    assert data["titulo"] == "Preparar informe trimestral"
    assert data["prioridad"] == "alta"
    assert data["estado"] == "pendiente"
    assert "creado_en" in data
    assert "actualizado_en" in data


def test_crear_tercera_tarea_prioridad_alta_retorna_400(client, db_session):
    """Verifica que intentar crear una 3ra tarea de prioridad alta responda HTTP 400 (Error Case 2)."""
    token, usuario = _crear_token_usuario(db_session, "user_limit@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Crear 1ra tarea alta
    res1 = client.post(
        "/tareas/", json={"titulo": "Alta 1", "prioridad": "alta"}, headers=headers
    )
    assert res1.status_code == 201

    # Crear 2da tarea alta
    res2 = client.post(
        "/tareas/", json={"titulo": "Alta 2", "prioridad": "alta"}, headers=headers
    )
    assert res2.status_code == 201

    # Intentar crear 3ra tarea alta -> debe fallar con 400
    res3 = client.post(
        "/tareas/", json={"titulo": "Alta 3", "prioridad": "alta"}, headers=headers
    )
    assert res3.status_code == 400
    assert "prioridad alta" in res3.json()["detail"]


def test_crear_tarea_esquema_invalido_retorna_422(client, db_session):
    """Verifica que títulos vacíos o prioridades inválidas respondan HTTP 422 (Error Case 1)."""
    token, _ = _crear_token_usuario(db_session, "user_val@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Título vacío
    res_vacio = client.post("/tareas/", json={"titulo": ""}, headers=headers)
    assert res_vacio.status_code == 422

    # Título compuesto solo por espacios
    res_espacios = client.post("/tareas/", json={"titulo": "   "}, headers=headers)
    assert res_espacios.status_code == 422

    # Prioridad inexistente
    res_prio = client.post(
        "/tareas/", json={"titulo": "Tarea", "prioridad": "urgente"}, headers=headers
    )
    assert res_prio.status_code == 422


def test_actualizar_estado_secuencia_valida(client, db_session):
    """Verifica actualización de estado válida de pendiente a en_progreso y luego a completada (HTTP 200)."""
    token, usuario = _crear_token_usuario(db_session, "user_flow@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Crear tarea (nace pendiente)
    crear_res = client.post(
        "/tareas/", json={"titulo": "Tarea de flujo"}, headers=headers
    )
    assert crear_res.status_code == 201
    tarea_id = crear_res.json()["id"]

    # Mover a en_progreso
    res_prog = client.patch(
        f"/tareas/{tarea_id}/estado",
        json={"estado": "en_progreso"},
        headers=headers,
    )
    assert res_prog.status_code == 200
    assert res_prog.json()["estado"] == "en_progreso"

    # Mover a completada
    res_comp = client.patch(
        f"/tareas/{tarea_id}/estado",
        json={"estado": "completada"},
        headers=headers,
    )
    assert res_comp.status_code == 200
    assert res_comp.json()["estado"] == "completada"


def test_actualizar_estado_limite_wip_retorna_400(client, db_session):
    """Verifica que mover una 4ta tarea a en_progreso retorne HTTP 400 LimiteWIPExcedidoError (Error Case 3)."""
    token, _ = _crear_token_usuario(db_session, "user_wip@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Crear 4 tareas
    ids = []
    for i in range(4):
        res = client.post("/tareas/", json={"titulo": f"Tarea WIP {i}"}, headers=headers)
        assert res.status_code == 201
        ids.append(res.json()["id"])

    # Mover 3 a en_progreso
    for tid in ids[:3]:
        r = client.patch(f"/tareas/{tid}/estado", json={"estado": "en_progreso"}, headers=headers)
        assert r.status_code == 200

    # Intentar mover la 4ta -> debe fallar con 400
    r_fail = client.patch(
        f"/tareas/{ids[3]}/estado",
        json={"estado": "en_progreso"},
        headers=headers,
    )
    assert r_fail.status_code == 400
    assert "en progreso" in r_fail.json()["detail"]


def test_actualizar_estado_transicion_invalida_retorna_400(client, db_session):
    """Verifica que saltar de pendiente a completada retorne HTTP 400 TransicionEstadoInvalidaError (Error Case 4)."""
    token, _ = _crear_token_usuario(db_session, "user_trans@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    crear_res = client.post(
        "/tareas/", json={"titulo": "Tarea salto directo"}, headers=headers
    )
    tarea_id = crear_res.json()["id"]

    # Intentar pasar directo a completada
    res = client.patch(
        f"/tareas/{tarea_id}/estado",
        json={"estado": "completada"},
        headers=headers,
    )
    assert res.status_code == 400
    assert "No se permite pasar de 'pendiente' a 'completada'" in res.json()["detail"]


def test_actualizar_estado_recurso_ajeno_retorna_403(client, db_session):
    """Verifica que modificar una tarea de otro usuario retorne HTTP 403 Forbidden (Error Case 6)."""
    token1, _ = _crear_token_usuario(db_session, "dueno@example.com")
    token2, _ = _crear_token_usuario(db_session, "atacante@example.com")

    # Usuario 1 crea la tarea
    crear_res = client.post(
        "/tareas/",
        json={"titulo": "Tarea protegida"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    tarea_id = crear_res.json()["id"]

    # Usuario 2 intenta actualizar estado
    res = client.patch(
        f"/tareas/{tarea_id}/estado",
        json={"estado": "en_progreso"},
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert res.status_code == 403
    assert "No tiene permiso" in res.json()["detail"]


def test_actualizar_estado_inexistente_retorna_404(client, db_session):
    """Verifica que modificar una tarea inexistente retorne HTTP 404 Not Found (Error Case 7)."""
    token, _ = _crear_token_usuario(db_session, "user_404@example.com")
    res = client.patch(
        "/tareas/999999/estado",
        json={"estado": "en_progreso"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 404
    assert "no encontrada" in res.json()["detail"]


def test_listar_tareas_api_con_filtros_y_orden(client, db_session):
    """Verifica GET /tareas/ con orden descendente, filtros de estado/prioridad y paginación."""
    token, usuario = _crear_token_usuario(db_session, "user_list_api@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Crear tareas con diferentes prioridades
    r1 = client.post("/tareas/", json={"titulo": "T1", "prioridad": "baja"}, headers=headers)
    r2 = client.post("/tareas/", json={"titulo": "T2", "prioridad": "alta"}, headers=headers)
    r3 = client.post("/tareas/", json={"titulo": "T3", "prioridad": "alta"}, headers=headers)

    # 1. Sin autenticación -> 401 (Error Case 5)
    assert client.get("/tareas/").status_code == 401

    # 2. Listar todas -> 3 tareas en orden descendente [T3, T2, T1]
    res_todas = client.get("/tareas/", headers=headers)
    assert res_todas.status_code == 200
    items = res_todas.json()
    assert len(items) == 3
    assert items[0]["id"] == r3.json()["id"]
    assert items[1]["id"] == r2.json()["id"]
    assert items[2]["id"] == r1.json()["id"]

    # 3. Paginación con limit=2
    res_pag = client.get("/tareas/?skip=0&limit=2", headers=headers)
    assert res_pag.status_code == 200
    assert len(res_pag.json()) == 2

    # 4. Filtro por prioridad
    res_filtro = client.get("/tareas/?prioridad=alta", headers=headers)
    assert res_filtro.status_code == 200
    assert len(res_filtro.json()) == 2
    assert all(t["prioridad"] == "alta" for t in res_filtro.json())


def test_obtener_tarea_por_id_api(client, db_session):
    """Verifica GET /tareas/{id} con 200, 401 (Error Case 5), 403 (Error Case 6) y 404 (Error Case 7)."""
    token1, user1 = _crear_token_usuario(db_session, "owner_get@example.com")
    token2, user2 = _crear_token_usuario(db_session, "stranger_get@example.com")

    # Crear tarea para user 1
    crear_res = client.post(
        "/tareas/", json={"titulo": "Tarea detalle"}, headers={"Authorization": f"Bearer {token1}"}
    )
    t_id = crear_res.json()["id"]

    # 1. Sin token -> 401
    assert client.get(f"/tareas/{t_id}").status_code == 401

    # 2. Dueño consulta -> 200
    res_ok = client.get(f"/tareas/{t_id}", headers={"Authorization": f"Bearer {token1}"})
    assert res_ok.status_code == 200
    assert res_ok.json()["id"] == t_id
    assert res_ok.json()["usuario_id"] == user1.id

    # 3. Usuario ajeno consulta -> 403 (Error Case 6)
    res_ajeno = client.get(f"/tareas/{t_id}", headers={"Authorization": f"Bearer {token2}"})
    assert res_ajeno.status_code == 403
    assert "No tiene permiso" in res_ajeno.json()["detail"]

    # 4. Tarea inexistente -> 404 (Error Case 7)
    res_inexistente = client.get("/tareas/888888", headers={"Authorization": f"Bearer {token1}"})
    assert res_inexistente.status_code == 404
    assert "no encontrada" in res_inexistente.json()["detail"]


def test_eliminar_tarea_api(client, db_session):
    """Verifica DELETE /tareas/{id} con 204 No Content, 401 (Error Case 5), 403 (Error Case 6) y 404 (Error Case 7)."""
    token1, _ = _crear_token_usuario(db_session, "owner_del@example.com")
    token2, _ = _crear_token_usuario(db_session, "stranger_del@example.com")

    # Crear tarea
    crear_res = client.post(
        "/tareas/", json={"titulo": "Tarea a borrar"}, headers={"Authorization": f"Bearer {token1}"}
    )
    t_id = crear_res.json()["id"]

    # 1. Sin token -> 401 (Error Case 5)
    assert client.delete(f"/tareas/{t_id}").status_code == 401

    # 2. Usuario ajeno intenta borrar -> 403 (Error Case 6)
    res_ajeno = client.delete(f"/tareas/{t_id}", headers={"Authorization": f"Bearer {token2}"})
    assert res_ajeno.status_code == 403
    assert "No tiene permiso" in res_ajeno.json()["detail"]

    # 3. Tarea inexistente -> 404 (Error Case 7)
    res_inex = client.delete("/tareas/777777", headers={"Authorization": f"Bearer {token1}"})
    assert res_inex.status_code == 404
    assert "no encontrada" in res_inex.json()["detail"]

    # 4. Dueño elimina con éxito -> 204 No Content
    res_del = client.delete(f"/tareas/{t_id}", headers={"Authorization": f"Bearer {token1}"})
    assert res_del.status_code == 204

    # 5. Consulta posterior debe retornar 404
    res_get = client.get(f"/tareas/{t_id}", headers={"Authorization": f"Bearer {token1}"})
    assert res_get.status_code == 404



