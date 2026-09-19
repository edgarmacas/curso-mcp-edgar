import logging
from mcp.server.fastmcp import FastMCP
from mcp.server.auth.settings import AuthSettings
try:
    from mcp.server.auth.middleware.auth_context import get_access_token
except ImportError:
    get_access_token = lambda: None

from app.config import settings
from app.database import SessionLocal
from app.mcp.auth import JWTTokenVerifier
from app.repositories import usuarios as usuarios_repository
from app.services import gastos as gastos_service
from app.utils.security import hash_password

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "gastos-server",
    streamable_http_path="/",
    token_verifier=JWTTokenVerifier(),
    auth=AuthSettings(
        issuer_url=settings.mcp_issuer_url,
        resource_server_url=settings.mcp_resource_url,
        required_scopes=["gastos"],
        validate_token_resource=False,
    ),
)


def _obtener_o_crear_usuario_demo(db):
    """Fallback documentado a usuario demo en modo stdio sin token (Artículo VI.4)."""
    email = settings.mcp_demo_email or settings.DEMO_USER_EMAIL
    usuario = usuarios_repository.obtener_por_email(db, email)
    if usuario is None:
        usuario = usuarios_repository.guardar(
            db, email, hash_password(settings.mcp_demo_password)
        )
    return usuario


def _resolver_usuario_actual(db):
    """Resuelve la identidad del usuario actual a partir del token JWT MCP o usuario demo."""
    access_token = None
    try:
        access_token = get_access_token()
    except Exception:
        access_token = None

    if access_token is None:
        return _obtener_o_crear_usuario_demo(db)

    usuario = None
    if access_token.subject:
        usuario = usuarios_repository.obtener_por_email(db, access_token.subject)
    if usuario is None:
        raise ValueError("El token no corresponde a ningún usuario registrado")
    return usuario


@mcp.tool()
def registrar_gasto(descripcion: str, monto: float, categoria: str) -> dict:
    """Registra un nuevo gasto financiero para el usuario autenticado.

    Aplica las reglas de negocio del sistema: monto mayor a cero, descripción no vacía,
    categoría válida ('comida', 'transporte', 'entretenimiento', 'otros') y límite máximo
    acumulado de 500.0 por categoría.
    """
    db = SessionLocal()
    try:
        usuario = _resolver_usuario_actual(db)
        return gastos_service.registrar_gasto(
            db, usuario.id, descripcion, monto, categoria
        )
    except (
        ValueError,
        gastos_service.CategoriaInvalidaError,
        gastos_service.LimiteExcedidoError,
    ) as e:
        logger.warning("Error de negocio en tool registrar_gasto: %s", e)
        return {"error": str(e)}
    except Exception as e:
        logger.exception("Error inesperado en tool registrar_gasto")
        return {"error": str(e)}
    finally:
        db.close()


@mcp.tool()
def listar_gastos(skip: int = 0, limit: int = 20) -> list[dict] | dict:
    """Recupera los gastos personales del usuario autenticado en lotes paginados.

    Permite controlar el offset ('skip' >= 0) y el tamaño de página ('limit' >= 1).
    """
    if skip < 0 or limit < 1:
        return {"error": "Parámetros de paginación inválidos (skip >= 0, limit >= 1)"}

    db = SessionLocal()
    try:
        usuario = _resolver_usuario_actual(db)
        return gastos_service.listar_gastos(db, usuario.id, skip=skip, limit=limit)
    except Exception as e:
        logger.exception("Error inesperado en tool listar_gastos")
        return {"error": str(e)}
    finally:
        db.close()


if __name__ == "__main__":
    mcp.run()
