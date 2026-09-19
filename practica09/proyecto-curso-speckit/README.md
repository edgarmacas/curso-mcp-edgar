# Sistema de Control de Gastos Personales

Sistema backend robusto para el control y seguimiento de gastos personales desarrollado con FastAPI, SQLAlchemy, Alembic y Model Context Protocol (MCP) bajo arquitectura en capas y estricto cumplimiento de la Constitución v1.0.0.

## 🚀 Requisitos y Tecnologías

- **Python**: 3.12+
- **FastAPI**: API REST moderna y de alto rendimiento.
- **SQLAlchemy 2.0**: ORM y mapeo de datos desacoplado.
- **Alembic**: Control de versiones y migraciones de esquemas de persistencia.
- **PyJWT & Passlib (Bcrypt)**: Autenticación OAuth2 Password Flow y hash seguro de contraseñas.
- **MCP SDK (<2)**: Exposición de herramientas para asistentes y agentes IA vía `streamable-http` y `stdio`.
- **Pytest & Pytest-Cov**: Suite de pruebas piramidal (unitarias, integración, API, contratos) con cobertura verificada.

---

## 📦 Instalación

1. Crear y activar el entorno virtual:
   ```bash
   uv venv .venv
   source .venv/bin/activate
   ```

2. Instalar dependencias fijadas:
   ```bash
   uv pip install -r requirements.txt
   ```

3. Configurar variables de entorno:
   ```bash
   cp .env.example .env
   ```

---

## 🗄️ Migraciones de Base de Datos (Alembic)

Para aplicar las migraciones y crear las tablas `usuarios` y `gastos`:

```bash
alembic upgrade head
```

Para revertir la migración inicial:
```bash
alembic downgrade base
```

---

## ⚡ Ejecución del Servidor

### API REST + Servidor MCP (streamable-http)
Inicia el servidor HTTP unificado (incluye la API REST bajo `/` y el endpoint MCP bajo `/mcp`):
```bash
uvicorn app.main:app --reload --port 8000
```

- Documentación interactiva Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Endpoint MCP streamable-http: [http://127.0.0.1:8000/mcp](http://127.0.0.1:8000/mcp)

### Servidor MCP en modo stdio (Fallback local para clientes de terminal/agentes)
```bash
python -m app.mcp.server
```

---

## 🧪 Pruebas Automatizadas y Cobertura

Ejecutar la suite completa de pruebas:
```bash
pytest
```

Ejecutar con reporte detallado de cobertura por capas (Artículo VII.3):
```bash
pytest --cov=app --cov-report=term-missing
```
