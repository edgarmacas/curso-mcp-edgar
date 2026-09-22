"""Configuración y punto de entrada del servidor MCP (Model Context Protocol)."""

import asyncio
from typing import Optional
from sqlalchemy.orm import Session
from mcp.server.mcpserver import MCPServer
from app.config import settings
from app.database import SessionLocal, Base, engine
from app.repositories.usuarios_repository import usuarios_repository
from app.services.auth_service import hash_password
from app.mcp.tools import register_tools


def _resolve_user(db: Session) -> int:
    """Busca o crea el usuario correspondiente a MCP_USER_EMAIL."""
    usuario = usuarios_repository.obtener_por_email(db, settings.MCP_USER_EMAIL)
    if not usuario:
        # Fallback documentado: registrar usuario de servicio para MCP stdio
        usuario = usuarios_repository.crear_usuario(
            db=db,
            email=settings.MCP_USER_EMAIL,
            password_hash=hash_password("McpServicePassword123!"),
        )
    return usuario.id


def get_stdio_user_id(db: Optional[Session] = None) -> int:
    """Resuelve la identidad del usuario para transporte stdio a partir de MCP_USER_EMAIL.

    Conforme al Artículo VI.4, si el usuario no existe en BD, se crea automáticamente como
    fallback documentado para garantizar la operatividad de clientes locales (Claude Desktop, etc.).
    """
    if db is not None:
        return _resolve_user(db)

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        return _resolve_user(session)


# Instancia central del servidor MCP
mcp_server = MCPServer(
    name="SistemaGestionTareas",
    version="1.0.0",
    instructions="Servidor MCP para la gestión de tareas personales con límites de capacidad WIP y prioridad alta.",
)

# Registro de herramientas
register_tools(mcp_server, get_stdio_user_id)


if __name__ == "__main__":
    asyncio.run(mcp_server.run_stdio_async())
