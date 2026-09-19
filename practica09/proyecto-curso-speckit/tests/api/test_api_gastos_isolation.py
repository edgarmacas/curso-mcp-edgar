import pytest
from app.repositories import usuarios as usuarios_repo
from app.repositories import gastos as gastos_repo


def test_caso_error_4_peticiones_sin_token_retornan_401(client):
    """Caso de Error 4: Peticiones a POST /gastos/ y GET /gastos/ sin header Authorization retornan HTTP 401."""
    res_post = client.post(
        "/gastos/",
        json={"descripcion": "Almuerzo", "monto": 15.0, "categoria": "comida"},
    )
    assert res_post.status_code == 401

    res_get = client.get("/gastos/")
    assert res_get.status_code == 401


def test_caso_error_4_token_invalido_retorna_401(client):
    """Peticiones con token manipulado o inválido retornan HTTP 401."""
    headers = {"Authorization": "Bearer token_falso_invalido"}
    res_post = client.post(
        "/gastos/",
        json={"descripcion": "Almuerzo", "monto": 15.0, "categoria": "comida"},
        headers=headers,
    )
    assert res_post.status_code == 401

    res_get = client.get("/gastos/", headers=headers)
    assert res_get.status_code == 401


def test_caso_error_5_usuario_id_manual_en_query_es_ignorado(client, db_session, auth_headers):
    """Caso de Error 5: Intentos de consultar gastos pasando ?usuario_id=99 son ignorados.

    Verifica que jamás se filtre por ese ID y solo se retornen los gastos del token autenticado.
    """
    u1 = usuarios_repo.guardar(db_session, "user1@isolation.com", "hash1")
    u2 = usuarios_repo.guardar(db_session, "user2@isolation.com", "hash2")

    # Guardar gastos para ambos usuarios
    gastos_repo.guardar(db_session, u1.id, "Gasto U1 - 1", 10.0, "comida")
    gastos_repo.guardar(db_session, u1.id, "Gasto U1 - 2", 20.0, "transporte")
    gastos_repo.guardar(db_session, u2.id, "Gasto U2 Privado", 50.0, "entretenimiento")

    h1 = auth_headers(usuario_id=u1.id, email=u1.email)

    # U1 intenta espiar los gastos de U2 pasando ?usuario_id=<u2.id>
    response = client.get(f"/gastos/?usuario_id={u2.id}", headers=h1)
    assert response.status_code == 200
    data = response.json()

    # Debe retornar exclusivamente los 2 gastos de U1
    assert len(data) == 2
    descripciones = [g["descripcion"] for g in data]
    assert "Gasto U1 - 1" in descripciones
    assert "Gasto U1 - 2" in descripciones
    assert "Gasto U2 Privado" not in descripciones


def test_caso_error_5_usuario_id_manual_en_body_es_ignorado(client, db_session, auth_headers):
    """Intentos de inyectar usuario_id en el payload JSON son ignorados por el sistema."""
    u1 = usuarios_repo.guardar(db_session, "creator@isolation.com", "hash1")
    u2 = usuarios_repo.guardar(db_session, "target@isolation.com", "hash2")

    h1 = auth_headers(usuario_id=u1.id, email=u1.email)

    # U1 envía usuario_id apuntando a U2 en el body
    response = client.post(
        "/gastos/",
        json={
            "descripcion": "Gasto inyectado",
            "monto": 30.0,
            "categoria": "comida",
            "usuario_id": u2.id,
        },
        headers=h1,
    )
    assert response.status_code == 201

    # Verificar que el gasto pertenece a U1 y NO a U2
    gastos_u1 = gastos_repo.listar(db_session, u1.id)
    gastos_u2 = gastos_repo.listar(db_session, u2.id)

    assert len(gastos_u1) == 1
    assert gastos_u1[0]["descripcion"] == "Gasto inyectado"
    assert len(gastos_u2) == 0


def test_aislamiento_de_limites_por_categoria_entre_usuarios(client, db_session, auth_headers):
    """Verificar que el acumulado de 490.0 en comida de un Usuario A no bloquea

    a un Usuario B con 0.0 en comida para registrar un gasto de 80.0.
    """
    user_a = usuarios_repo.guardar(db_session, "usera@limits.com", "hashA")
    user_b = usuarios_repo.guardar(db_session, "userb@limits.com", "hashB")

    # Usuario A acumula 490.0 en 'comida'
    gastos_repo.guardar(db_session, user_a.id, "Comida A1", 400.0, "comida")
    gastos_repo.guardar(db_session, user_a.id, "Comida A2", 90.0, "comida")

    headers_a = auth_headers(usuario_id=user_a.id, email=user_a.email)
    headers_b = auth_headers(usuario_id=user_b.id, email=user_b.email)

    # Usuario B (con 0.0 acumulado) registra un gasto de 80.0 en 'comida' -> DEBE SER EXITOSO (201)
    res_b = client.post(
        "/gastos/",
        json={"descripcion": "Almuerzo Usuario B", "monto": 80.0, "categoria": "comida"},
        headers=headers_b,
    )
    assert res_b.status_code == 201
    assert res_b.json()["monto"] == 80.0

    # Usuario A intenta registrar 20.0 más en 'comida' (490 + 20 = 510 > 500) -> DEBE SER RECHAZADO (400)
    res_a = client.post(
        "/gastos/",
        json={"descripcion": "Postre Usuario A", "monto": 20.0, "categoria": "comida"},
        headers=headers_a,
    )
    assert res_a.status_code == 400
    assert "supera el límite de 500.0" in res_a.json()["detail"]


def test_auditoria_esquemas_y_rutas_sin_usuario_id_cliente():
    """T025 / Art. IV.4: Asegurar que ningún esquema de entrada ni endpoint

    exponga o acepte usuario_id como parámetro de entrada del cliente.
    """
    from app.schemas.gasto import GastoCreate
    from app.routers.gastos import router
    import inspect

    # GastoCreate no debe contener usuario_id
    assert "usuario_id" not in GastoCreate.model_fields

    # Ninguna función de router debe exponer usuario_id como parámetro sin Depends(get_current_user)
    for route in router.routes:
        sig = inspect.signature(route.endpoint)
        params = list(sig.parameters.keys())
        assert "usuario_id" not in params, f"Route {route.path} expone parámetro usuario_id directamente"
