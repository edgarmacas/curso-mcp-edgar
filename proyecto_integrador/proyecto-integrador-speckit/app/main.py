"""Punto de entrada principal de la aplicación FastAPI."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.database import Base, engine
from app.routers.usuarios import router as usuarios_router
from app.routers.tareas import router as tareas_router
from app.mcp.server import mcp_server

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Asegura esquemas de base de datos creados en el ciclo de vida de la app
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Sistema de gestión de tareas personales con límite de capacidad (WIP limits).",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Manejador global de excepciones no controladas conforme al Artículo IV.5."""
    if isinstance(exc, (HTTPException, RequestValidationError)):
        raise exc
    logger.exception("Excepción no controlada interceptada: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"},
    )


# Inclusión de routers REST
app.include_router(usuarios_router)
app.include_router(tareas_router)

# Montaje de transporte MCP streamable-http
app.mount("/mcp", mcp_server.streamable_http_app())


@app.get("/health", tags=["sistema"])
def health_check():
    """Endpoint de verificación de estado y salud del servicio."""
    return {"status": "ok", "app": settings.APP_NAME}
