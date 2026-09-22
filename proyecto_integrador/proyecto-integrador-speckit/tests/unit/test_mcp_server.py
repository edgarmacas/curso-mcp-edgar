"""Pruebas unitarias para la configuración del servidor MCP en app/mcp/server.py."""

import pytest
from app.mcp.server import get_stdio_user_id, mcp_server
from app.config import settings
from app.repositories.usuarios_repository import usuarios_repository


def test_get_stdio_user_id_creates_and_resolves(db_session):
    """Verifica que get_stdio_user_id cree el usuario fallback si no existe y luego lo resuelva."""
    # Primer llamado: crea el usuario
    uid1 = get_stdio_user_id(db=db_session)
    assert uid1 is not None

    usuario = usuarios_repository.obtener_por_email(db_session, settings.MCP_USER_EMAIL)
    assert usuario is not None
    assert usuario.id == uid1
    assert usuario.email == settings.MCP_USER_EMAIL

    # Segundo llamado: no debe crear duplicado, retorna el mismo ID
    uid2 = get_stdio_user_id(db=db_session)
    assert uid2 == uid1


@pytest.mark.asyncio
async def test_mcp_server_has_tools_registered():
    """Verifica que la instancia mcp_server tenga registradas las 3 herramientas requeridas."""
    tools = await mcp_server.list_tools()
    nombres = [t.name for t in tools]
    assert "crear_tarea" in nombres
    assert "listar_tareas" in nombres
    assert "iniciar_tarea_prioritaria" in nombres
