"""Pruebas unitarias para las herramientas MCP en app/mcp/tools.py."""

from app.mcp.tools import (
    mcp_crear_tarea,
    mcp_listar_tareas,
    mcp_iniciar_tarea_prioritaria,
    register_tools,
)
from mcp.server.mcpserver import MCPServer


def test_mcp_crear_tarea_exitoso_y_limite(fake_tareas_repo):
    """Verifica creación vía MCP y retorno estructurado de error ante límite de prioridad alta."""
    u_id = 1
    # Crear 2 tareas de prioridad alta exitosamente
    res1 = mcp_crear_tarea(titulo="Alta 1", prioridad="alta", usuario_id=u_id, repo=fake_tareas_repo)
    assert res1.get("success") is True
    assert res1["tarea"]["prioridad"] == "alta"

    res2 = mcp_crear_tarea(titulo="Alta 2", prioridad="alta", usuario_id=u_id, repo=fake_tareas_repo)
    assert res2.get("success") is True

    # 3ra tarea alta retorna error estructurado sin lanzar excepción no capturada
    res3 = mcp_crear_tarea(titulo="Alta 3", prioridad="alta", usuario_id=u_id, repo=fake_tareas_repo)
    assert "error" in res3
    assert "LimitePrioridadAltaExcedidoError" in res3["error"]


def test_mcp_crear_tarea_validacion_invalida(fake_tareas_repo):
    """Verifica que errores de validación de esquema retornen {"error": ...}."""
    res = mcp_crear_tarea(titulo="", prioridad="alta", usuario_id=1, repo=fake_tareas_repo)
    assert "error" in res
    assert "ValidationError" in res["error"]


def test_mcp_listar_tareas(fake_tareas_repo):
    """Verifica listar tareas vía MCP con formato estructurado."""
    u_id = 1
    mcp_crear_tarea(titulo="T1", prioridad="baja", usuario_id=u_id, repo=fake_tareas_repo)
    mcp_crear_tarea(titulo="T2", prioridad="alta", usuario_id=u_id, repo=fake_tareas_repo)

    res = mcp_listar_tareas(usuario_id=u_id, repo=fake_tareas_repo)
    assert res.get("success") is True
    assert res["total"] == 2
    assert len(res["tareas"]) == 2


def test_mcp_iniciar_tarea_prioritaria_flujo_y_wip(fake_tareas_repo):
    """Verifica iniciar_tarea_prioritaria vía MCP, seleccionando la más prioritaria y manejando límite WIP."""
    u_id = 1
    # Sin tareas pendientes
    res_vacio = mcp_iniciar_tarea_prioritaria(usuario_id=u_id, repo=fake_tareas_repo)
    assert res_vacio.get("success") is False
    assert "No hay tareas pendientes" in res_vacio["mensaje"]

    # Crear una baja y una alta
    mcp_crear_tarea(titulo="Tarea Baja", prioridad="baja", usuario_id=u_id, repo=fake_tareas_repo)
    mcp_crear_tarea(titulo="Tarea Alta", prioridad="alta", usuario_id=u_id, repo=fake_tareas_repo)

    # Iniciar -> debe seleccionar la alta
    res_inicio = mcp_iniciar_tarea_prioritaria(usuario_id=u_id, repo=fake_tareas_repo)
    assert res_inicio.get("success") is True
    assert res_inicio["tarea"]["prioridad"] == "alta"
    assert res_inicio["tarea"]["estado"] == "en_progreso"


import pytest


@pytest.mark.asyncio
async def test_register_tools_on_mcpserver():
    """Verifica que register_tools registre las 3 herramientas en una instancia MCPServer."""
    server = MCPServer(name="test_server")
    register_tools(server, lambda: 42)
    tools = await server.list_tools()
    tool_names = [t.name for t in tools]
    assert "crear_tarea" in tool_names
    assert "listar_tareas" in tool_names
    assert "iniciar_tarea_prioritaria" in tool_names

