import pytest
from app.mcp.server import registrar_gasto, listar_gastos, mcp
from app.database import Base, engine, SessionLocal
from app.repositories import gastos as gastos_repo
from app.repositories import usuarios as usuarios_repo
from app.config import settings


@pytest.fixture(autouse=True)
def init_db(db_session):
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


@pytest.mark.anyio
async def test_mcp_registrar_gasto_exito():
    """Tool registrar_gasto: éxito registrando gasto para usuario."""
    resultado = registrar_gasto("Taxi al aeropuerto", 35.0, "transporte")
    assert isinstance(resultado, dict)
    assert "error" not in resultado
    assert resultado["descripcion"] == "Taxi al aeropuerto"
    assert resultado["monto"] == 35.0
    assert resultado["categoria"] == "transporte"


@pytest.mark.anyio
async def test_mcp_registrar_gasto_categoria_invalida():
    """Tool registrar_gasto: captura error de negocio ante categoría inexistente."""
    resultado = registrar_gasto("Viaje espacial", 50.0, "aeronautica")
    assert isinstance(resultado, dict)
    assert "error" in resultado
    assert "no es una categoría válida" in resultado["error"]


@pytest.mark.anyio
async def test_mcp_registrar_gasto_limite_excedido():
    """Tool registrar_gasto: captura error de negocio ante superación de límite de 500."""
    db = SessionLocal()
    try:
        email = settings.mcp_demo_email or settings.DEMO_USER_EMAIL
        usuario = usuarios_repo.obtener_por_email(db, email)
        if not usuario:
            usuario = usuarios_repo.guardar(db, email, "hash")
        # Acumular 480 en 'comida'
        gastos_repo.guardar(db, usuario.id, "Banquete 1", 480.0, "comida")
    finally:
        db.close()

    # Intentar registrar 30 más (480 + 30 = 510 > 500)
    resultado = registrar_gasto("Postre de lujo", 30.0, "comida")
    assert isinstance(resultado, dict)
    assert "error" in resultado
    assert "supera el límite de 500.0" in resultado["error"]


@pytest.mark.anyio
async def test_mcp_listar_gastos_paginacion():
    """Tool listar_gastos: éxito listando gastos con paginación skip y limit."""
    db = SessionLocal()
    try:
        email = settings.mcp_demo_email or settings.DEMO_USER_EMAIL
        usuario = usuarios_repo.obtener_por_email(db, email)
        if not usuario:
            usuario = usuarios_repo.guardar(db, email, "hash")
        for i in range(5):
            gastos_repo.guardar(db, usuario.id, f"Gasto MCP {i}", 10.0 + i, "otros")
    finally:
        db.close()

    gastos_pag = listar_gastos(skip=1, limit=2)
    assert isinstance(gastos_pag, list)
    assert len(gastos_pag) == 2


@pytest.mark.anyio
async def test_mcp_listar_gastos_parametros_invalidos():
    """Tool listar_gastos: manejo de parámetros inválidos devolviendo error estructurado."""
    res_skip = listar_gastos(skip=-5, limit=10)
    assert isinstance(res_skip, dict)
    assert "error" in res_skip
    assert "Parámetros de paginación inválidos" in res_skip["error"]

    res_limit = listar_gastos(skip=0, limit=0)
    assert isinstance(res_limit, dict)
    assert "error" in res_limit
    assert "Parámetros de paginación inválidos" in res_limit["error"]


@pytest.mark.anyio
async def test_mcp_call_tool_interface():
    """Invocación a través del protocolo call_tool de FastMCP."""
    contents = await mcp.call_tool(
        "registrar_gasto",
        {"descripcion": "Cine MCP", "monto": 14.50, "categoria": "entretenimiento"},
    )
    assert len(contents) > 0
    assert "Cine MCP" in contents[0].text
