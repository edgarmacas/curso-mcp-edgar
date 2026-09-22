# Implementation Plan: Sistema de Gestión de Tareas Personales con Límite de Capacidad (WIP Limits)

**Branch**: `001-task-wip-limits` | **Date**: 2026-09-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-task-wip-limits/spec.md`

## Summary

Construcción de un backend de alto rendimiento y arquitectura limpia para la gestión personal de tareas con control estricto de capacidad (máximo 2 tareas de prioridad alta abiertas simultáneamente, máximo 3 tareas en progreso como límite WIP, y transiciones de estado restringidas `pendiente` -> `en_progreso` -> `completada`). La solución expone dos interfaces concurrentes: una API REST moderna con FastAPI y una interfaz agéntica mediante el protocolo estándar MCP (Model Context Protocol) montado sobre transporte HTTP streamable y stdio. Ambas interfaces comparten de forma transparente y estricta la misma capa de servicios de dominio, garantizando aislamiento multi-inquilino, inyección de dependencias (DIP) para testing sin mocks y cumplimiento del 100% de los principios constitucionales.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**:
- `fastapi` & `uvicorn[standard]` (Framework HTTP asíncrono y servidor ASGI)
- `sqlalchemy` (ORM agnóstico y query builder) & `alembic` (migraciones de base de datos)
- `pydantic` & `pydantic-settings` (validación de esquemas y configuración tipada vía `.env`)
- `email-validator` (validación estricta de formato de correo electrónico)
- `python-multipart` (soporte para OAuth2 password form en login)
- `pyjwt` (generación y verificación de tokens JWT con algoritmo HS256)
- `passlib[bcrypt]` con fijación `bcrypt<4.1` (hashing seguro de contraseñas)
- `mcp` (SDK oficial de Model Context Protocol para exposición de tools)

**Storage**:
- SQLite para entornos de desarrollo y testing local (con `connect_args={"check_same_thread": False}`).
- Diseño desacoplado y agnóstico en `app/database.py` para compatibilidad nativa con PostgreSQL en producción.

**Testing**:
- `pytest`, `pytest-cov`, `pytest-asyncio`, `httpx` (cliente de pruebas asíncrono para endpoints REST y MCP).
- Base de datos SQLite en memoria para tests de integración.
- Repositorios falsos en memoria (`FakeTareasRepository`) para tests unitarios bajo DIP (sin `unittest.mock`).

**Target Platform**: Linux Server / Contenedores Docker / Local Workstation

**Project Type**: Servicio Web Híbrido (REST API + MCP Server)

**Performance Goals**:
- Tiempo de respuesta < 200 ms (p95) en endpoints REST y llamadas a tools MCP en entorno local.
- Tiempo de ejecución de suite de pruebas unitarias < 3 segundos.

**Constraints**:
- Prohibición estricta de `unittest.mock` en tests unitarios de `services/` (inyección obligatoria por DIP).
- Cobertura de código obligatoria: 100% de reglas de negocio en `spec.md`, $\ge 90\%$ de líneas en `services/`, $\ge 70\%$ global combinada (`services` + `repositories` + `routers` + `utils`).
- Prohibición de importar SQLAlchemy o `Session` dentro de `services/`.
- Autorización estricta: `usuario_id` siempre derivado del token verificado o sesión MCP autenticada, nunca del cliente.

**Scale/Scope**:
- Aplicación de gestión personal de tareas con aislamiento multi-usuario.
- Soporte para miles de tareas por usuario y concurrencia fluida en FastAPI.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artículo | Principio Constitucional | Estado en Plan | Mecanismo de Cumplimiento |
|---|---|---|---|
| **I.1** | `routers/` solo traducen HTTP y no validan negocio | PASS | Los routers en `app/routers/` delegan 100% al service; capturan excepciones de dominio y retornan respuestas HTTP semánticas. |
| **I.2** | `services/` contienen toda la lógica y no importan SQLAlchemy | PASS | `app/services/` encapsula validación de límites (WIP, prioridad alta) y transiciones; recibe modelos/DTOs sin importar SQLAlchemy ni `Session`. |
| **I.3** | `repositories/` son la única capa con persistencia a BD | PASS | `app/repositories/` realiza operaciones de persistencia filtrando siempre por `usuario_id`; no contiene reglas de negocio. |
| **I.4** | `utils/` son funciones puras | PASS | `app/utils/` alberga formateadores y utilidades deterministas sin efectos secundarios ni dependencias de dominio. |
| **I.5** | `mcp/` reutiliza `services/` sin duplicar lógica | PASS | Tools en `app/mcp/tools.py` llaman a las mismas funciones en `app/services/tareas_service.py` que invocan los routers. |
| **II.1** | SRP en services | PASS | Funciones de validación de límites desacopladas de la creación/actualización en `tareas_service.py`. |
| **II.2** | OCP mediante Enums | PASS | `PrioridadEnum` y `EstadoEnum` modelados como Enums nativos en `app/models/` y `app/schemas/`. |
| **II.3** | DIP con valor por defecto en services | PASS | Firmas `def crear_tarea(..., repo=tareas_repository)` para permitir inyección directa de repositorios falsos sin `unittest.mock`. |
| **III.1** | SQLAlchemy agnóstico | PASS | Configuración en `app/database.py` condicional al dialecto SQLite/PostgreSQL. |
| **III.2** | Aislamiento por `usuario_id` en `Tarea` | PASS | Clave foránea `usuario_id` en modelo `Tarea` e inclusión obligatoria de `usuario_id` en todas las consultas de repositorio. |
| **IV.1-6** | Seguridad estricta (bcrypt<4.1, JWT HS256, .env, autorización token) | PASS | Passwords hasheadas con `passlib[bcrypt]` (`bcrypt<4.1`), JWT con expiración, lectura de secretos vía `pydantic-settings`, nunca aceptar `usuario_id` del cliente, 500 genérico. |
| **V.1-3** | Endpoints REST semánticos y esquemas separados | PASS | Códigos 201, 200, 204, 400, 401, 403, 404, 422; esquemas `TareaCreate` vs `TareaOut`; paginación con `skip`/`limit`. |
| **VI.1-5** | Protocolo MCP robusto | PASS | Respuestas de error `{"error": "..."}`, resolución de usuario por sesión (y fallback `MCP_USER_EMAIL` en stdio). |
| **VII.1-4** | Pirámide de pruebas y cobertura estricta | PASS | Unitarias con `FakeTareasRepository` (sin mock), integración en memoria, API con `dependency_overrides`. Cobertura $\ge 90\%$ services, $\ge 70\%$ global. |

## Project Structure

### Documentation (this feature)

```text
specs/001-task-wip-limits/
├── plan.md              # Este documento de planificación
├── research.md          # Investigación técnica y decisiones de arquitectura
├── data-model.md        # Definición de entidades, DTOs, Enums e invariantes
├── quickstart.md        # Guía de validación y ejecución paso a paso
├── contracts/           # Especificación de interfaces públicas
│   ├── api-rest.md      # Contrato de endpoints REST y respuestas HTTP
│   └── mcp-tools.md     # Contrato de herramientas MCP y esquemas de payload
└── tasks.md             # Tareas de descomposición (fase siguiente)
```

### Source Code (repository root)

```text
app/
├── __init__.py
├── main.py                     # Punto de entrada FastAPI, montaje de routers y server MCP
├── config.py                   # Pydantic Settings (.env, DATABASE_URL, SECRET_KEY, JWT_EXPIRE)
├── database.py                 # Engine SQLAlchemy, SessionLocal y Base declarativa
├── models/                     # Modelos ORM SQLAlchemy
│   ├── __init__.py
│   ├── usuario.py              # Modelo Usuario (id, email, password_hash, creado_en)
│   └── tarea.py                # Modelo Tarea (id, usuario_id FK, titulo, prioridad, estado, ...)
├── schemas/                    # DTOs y validación Pydantic
│   ├── __init__.py
│   ├── usuario.py              # UsuarioCreate, UsuarioOut
│   ├── tarea.py                # TareaCreate, TareaUpdateEstado, TareaOut, PrioridadEnum, EstadoEnum
│   └── token.py                # TokenOut, TokenData
├── repositories/               # Capa exclusiva de persistencia (SQLAlchemy queries)
│   ├── __init__.py
│   ├── usuarios_repository.py  # Operaciones DB para Usuario (crear, buscar por email/id)
│   └── tareas_repository.py    # Operaciones DB para Tarea (crear, listar, buscar, contar, eliminar)
├── services/                   # Lógica pura de negocio y validación de reglas
│   ├── __init__.py
│   ├── exceptions.py           # LimitePrioridadAltaExcedidoError, LimiteWIPExcedidoError, etc.
│   ├── auth_service.py         # Hashing, verificación y generación de JWT
│   └── tareas_service.py       # Orquestación y validaciones de tareas (con DIP por defecto)
├── routers/                    # Endpoints HTTP FastAPI
│   ├── __init__.py
│   ├── deps.py                 # get_db, get_current_user (OAuth2Bearer)
│   ├── usuarios.py             # POST /usuarios/, POST /usuarios/token
│   └── tareas.py               # POST, GET, PATCH, DELETE /tareas/
├── mcp/                        # Servidor MCP y herramientas
│   ├── __init__.py
│   ├── server.py               # Inicialización y montaje streamable-http en FastAPI
│   └── tools.py                # Tools crear_tarea, listar_tareas, iniciar_tarea_prioritaria
└── utils/                      # Funciones puras
    ├── __init__.py
    └── date_utils.py           # Utilidades puras de fecha y normalización ISO

tests/
├── __init__.py
├── conftest.py                 # Fixtures SQLite en memoria, cliente TestClient y usuarios de prueba
├── fakes/                      # Repositorios en memoria para DIP
│   ├── __init__.py
│   └── fake_tareas_repository.py # Implementación falsa en memoria para pruebas unitarias sin mock
├── unit/                       # Pruebas unitarias de servicios (DIP, sin unittest.mock)
│   ├── __init__.py
│   └── test_services_tareas.py # 100% reglas de negocio (WIP, prioridad alta, transiciones)
├── integration/                # Pruebas de repositorios contra SQLite real
│   ├── __init__.py
│   └── test_repositories.py
└── api/                        # Pruebas de integración HTTP y MCP con dependency_overrides
    ├── __init__.py
    ├── test_auth_api.py
    ├── test_tareas_api.py
    └── test_mcp_api.py
```

**Structure Decision**: Se implementa una estructura monolítica modular bajo el paquete `app/`, aplicando una clara separación de responsabilidades unidireccional: `routers/` y `mcp/` $\to$ `services/` $\to$ `repositories/` $\to$ `database.py`. Los servicios se mantienen desacoplados de la persistencia gracias al principio DIP, garantizando pruebas unitarias limpias y un servidor MCP completamente integrado.

## Complexity Tracking

> **Alineación total con la Constitución: no existen violaciones que requieran justificación excepcional.**

| Componente / Patrón | Necesidad y Justificación | Alternativa Más Simple Evaluada y Razón de Descarte |
|---|---|---|
| **Repositorios con DIP** | Exigido por Artículo II.3 para posibilitar tests unitarios puros sin `unittest.mock`. | Consultas SQLAlchemy directas en services: Rechazada porque acopla la lógica de negocio al ORM y fuerza el uso de mocks complejos. |
| **Separación de DTOs Pydantic** | Exigido por Artículos IV.6 y V.3 para evitar sobre-exposición de campos del modelo ORM (ej. `password_hash`). | Retornar modelos SQLAlchemy directamente: Rechazada por riesgo de fuga de seguridad e inconsistencias de serialización. |
| **Montaje Streamable HTTP de MCP** | Permite exponer el protocolo MCP en el mismo proceso FastAPI en producción o como stdio en desarrollo. | Servidor MCP en proceso separado con duplicación de lógica: Rechazada por violación del Artículo VI.1 (reutilización de services). |
