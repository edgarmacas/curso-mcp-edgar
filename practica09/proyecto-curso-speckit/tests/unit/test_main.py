import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_app_instance():
    assert app.title == "API de Control de Gastos"
    # Verificar que /mcp está montado
    rutas_montadas = [getattr(route, "path", None) for route in app.routes]
    assert "/mcp" in rutas_montadas

def test_error_no_controlado_retorna_500_generico():
    # Creamos una ruta de prueba temporal que lance un error inesperado
    @app.get("/test-error-inesperado")
    def ruta_que_falla():
        raise RuntimeError("Fallo catastrófico de prueba interno")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/test-error-inesperado")
        assert response.status_code == 500
        assert response.json() == {"detail": "Error interno del servidor"}
        # Verificar que no expone el stack trace ni el mensaje original al cliente (Art. IV.5)
        assert "Fallo catastrófico" not in response.text
