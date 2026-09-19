# Implementation Plan: Sistema de Control de Gastos Personales

**Branch**: `001-control-gastos` | **Date**: 2026-09-19 | **Spec**: [specs/001-control-gastos/spec.md](spec.md)

**Input**: Feature specification from `specs/001-control-gastos/spec.md` y directivas de la Constitución v1.0.0.

---

## Summary

Implementar un sistema modular de control de gastos personales con doble interfaz (API REST y servidor MCP vía streamable-http) en FastAPI. El sistema garantiza una arquitectura limpia en capas (`routers/`, `services/`, `repositories/`, `utils/`, `mcp/`), persistencia con SQLAlchemy y Alembic, autenticación mediante OAuth2 Password Flow + JWT firmado con `pyjwt`, hashing de contraseñas con `passlib[bcrypt]` (`bcrypt<4.1`), y cumplimiento riguroso de reglas de negocio: validación de categorías (`comida`, `transporte`, `entretenimiento`, `otros`), montos estrictamente positivos y límite acumulado de 500.0 por categoría y usuario. La arquitectura adopta inversión de dependencias simple (DIP) con parámetros por defecto para permitir testing unitario sin `unittest.mock`.

---

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**:
- Web & Framework: `fastapi`, `uvicorn[standard]`
- Persistencia & Migraciones: `sqlalchemy>=2.0`, `alembic`
- Seguridad & Autenticación: `pyjwt`, `passlib[bcrypt]`, `bcrypt>=4.0.1,<4.1.0`, `python-multipart`
- Configuración & Validación: `pydantic-settings`, `email-validator`
- Protocolo MCP: `mcp` (SDK oficial con transporte streamable-http montado en FastAPI)
- Testing: `pytest`, `pytest-cov`, `httpx`

**Storage**: SQLite en desarrollo y pruebas de integración (en memoria: `sqlite:///:memory:`). Arquitectura desacoplada en `database.py` preparada para PostgreSQL en producción sin alterar servicios ni repositorios.

**Testing**: Pytest con tres capas: Unitarias (`tests/unit/` con repositorios falsos inyectados), Integración (`tests/integration/` con SQLite real en memoria) y API/MCP (`tests/api/` usando `TestClient` y `app.dependency_overrides`). Cobertura exigida: 100% reglas de negocio, $\ge 90\%$ en `services/`, $\ge 80\%$ global (`services + repositories + routers + utils`).

**Target Platform**: Linux server / Contenedor Docker / Entornos Cloud compatibles con ASGI.

**Project Type**: Servicio Web REST + Servidor Asistente MCP (`web-service`).

**Performance Goals**: Latencia inferior a 200ms en el percentil 95 (p95) para operaciones de autenticación, creación y listado de gastos.

**Constraints**:
- Prohibición de reglas de negocio en routers y repositorios.
- Prohibición de importar SQLAlchemy/Session en `services/`.
- Inyección de dependencias (DIP) por parámetro keyword con valor por defecto (`repo=gastos_repository`). Prohibido `unittest.mock`.
- Aislamiento estricto: el `usuario_id` siempre proviene del token JWT decodificado (`get_current_user`), nunca de parámetros manipulables.
- Formato de errores no controlados: HTTP 500 con `{"detail": "Error interno del servidor"}`.
- Compatibilidad retroactiva estricta con firmas y contratos de las Sesiones 6-8.

**Scale/Scope**: 5 historias de usuario, 2 entidades relacionales (`Usuario`, `Gasto`), 4 categorías canónicas, 1 límite financiero acumulado por categoría (500.0).

---

## Constitution Check

*GATE: Evaluado antes del diseño y re-evaluado post-diseño.*

| Artículo Constitucional | Requisito Principal | Estado en Plan | Mecanismo de Cumplimiento |
|-------------------------|---------------------|----------------|---------------------------|
| **I. Arquitectura en capas** | Separación estricta de carpetas sin imports inversos | ✅ PASS | Paquetes separados bajo `app/`. `routers/` delegan a `services/`. `services/` no tocan SQLAlchemy. `repositories/` son la única capa DB. `utils/` puras. |
| **II. SOLID aplicado** | SRP, OCP, DIP vía parámetros por defecto | ✅ PASS | Validación (`_validar_x`) separada de orquestación (`registrar_x`). OCP con tuplas/constantes. DIP con `repo=gastos_repository`. |
| **III. Persistencia** | ORM SQLAlchemy, Alembic, SQLite/Postgres agnóstico, FK y filtro `usuario_id` | ✅ PASS | Cero SQL concatenado. `connect_args` condicional solo para SQLite. Modelos con FK `usuario_id` y consultas filtradas obligatoriamente. |
| **IV. Seguridad** | Hashing bcrypt (<4.1), JWT HS256 con pyjwt, secretos en `.env`, ID exclusivo de JWT | ✅ PASS | `passlib[bcrypt]` con `bcrypt<4.1`. `pydantic-settings` para `.env`. `get_current_user` inyecta `usuario_id`. Manejador global de 500 genérico. |
| **V. Endpoints REST** | Verbos y códigos (201, 200, 400, 401, 404, 422), paginación skip/limit, DTOs Pydantic | ✅ PASS | Códigos exactos implementados. `GastoCreate` y `GastoOut` independientes de SQLAlchemy. Paginación validada con 422 si inválida. |
| **VI. MCP Tools** | Reutilización de services, errores estructurados, transporte streamable-http | ✅ PASS | Tools montadas en `/mcp` llaman directamente a `services.gastos.*`. Retornan `{"error": "..."}` ante fallos de negocio. |
| **VII. Testing** | Pirámide de pruebas, `RepositorioFalso`, cobertura $\ge 90\%$ services, $\ge 80\%$ global | ✅ PASS | Fixtures en `tests/`. Prohibido `unittest.mock`. SQLite en memoria en integración. `pytest-cov` configurado para validar umbrales. |
| **VIII. Compatibilidad** | Firmas inmutables de Sesiones 6-8, repositorios funcionales | ✅ PASS | Repositorios son módulos con funciones sueltas que devuelven `dict` o entidades. Tests de Sesiones 6-8 se integran inmutables. |

---

## Project Structure

### Documentation (this feature)

```text
specs/001-control-gastos/
├── plan.md              # Este archivo (plan de arquitectura y decisiones)
├── research.md          # Investigación técnica y decisiones arquitectónicas
├── data-model.md        # Definición de entidades, esquemas y relaciones
├── quickstart.md        # Guía de ejecución, pruebas y validación E2E
├── contracts/           # Contratos formales de interfaces
│   ├── rest-api.md      # Contrato de endpoints HTTP / REST
│   └── mcp-tools.md     # Contrato de herramientas MCP
└── checklists/
    └── requirements.md  # Checklist de calidad de especificación
```

### Source Code (repository root)

```text
app/
├── __init__.py
├── main.py                  # Entrypoint FastAPI, manejadores globales de error, montaje MCP
├── config.py                # Configuración vía pydantic-settings (.env)
├── database.py              # Engine SQLAlchemy, SessionLocal, get_db
├── dependencies.py          # get_current_user, get_gastos_repo
├── models/
│   ├── __init__.py
│   ├── usuario.py           # Modelo SQLAlchemy Usuario
│   └── gasto.py             # Modelo SQLAlchemy Gasto
├── schemas/
│   ├── __init__.py
│   ├── usuario.py           # UsuarioCreate, UsuarioOut, Token
│   └── gasto.py             # GastoCreate, GastoOut
├── repositories/
│   ├── __init__.py
│   ├── usuarios.py          # obtener_por_email, guardar (funciones sueltas)
│   └── gastos.py            # guardar, listar, total_por_categoria (funciones sueltas)
├── services/
│   ├── __init__.py
│   ├── auth.py              # autenticar_usuario, registrar_usuario
│   └── gastos.py            # CategoriaInvalidaError, LimiteExcedidoError, registrar_gasto, listar_gastos
├── routers/
│   ├── __init__.py
│   ├── usuarios.py          # POST /usuarios/, POST /usuarios/token
│   └── gastos.py            # POST /gastos/, GET /gastos/
├── utils/
│   ├── __init__.py
│   └── security.py          # Funciones puras: hash_password, verify_password, create_access_token, decode_token
└── mcp/
    ├── __init__.py
    └── server.py            # Servidor MCP, tools registrar_gasto, listar_gastos

alembic/                     # Migraciones de base de datos
├── env.py
├── script.py.mako
└── versions/

alembic.ini                  # Configuración de Alembic

tests/
├── __init__.py              # Requerido explícitamente para imports relativos
├── conftest.py              # Fixtures compartidas (db en memoria, tokens, test client)
├── test_gastos.py           # Test original de Sesiones 6-8 (define RepositorioFalso)
├── test_api_gastos.py       # Test API original de Sesiones 6-8
├── unit/
│   ├── test_services_gastos.py
│   └── test_services_auth.py
├── integration/
│   ├── test_repo_gastos.py
│   └── test_repo_usuarios.py
└── api/
    ├── test_api_usuarios.py
    ├── test_api_gastos_isolation.py
    └── test_mcp_tools.py
```

**Structure Decision**: Se adopta un proyecto único modular en Python (`app/`) con distribución estricta de responsabilidades en subpaquetes y separación clara de pruebas por nivel en la pirámide de testing (`tests/unit/`, `tests/integration/`, `tests/api/`).

---

## Complexity Tracking

> No se registran violaciones ni desvíos respecto a la Constitución del proyecto. Toda la arquitectura se alinea al 100% con los ocho artículos constitucionales y con los contratos de las Sesiones 6-8.
