# Implementation Tasks: Sistema de Gestión de Tareas Personales con Límite de Capacidad (WIP Limits)

**Feature**: `001-task-wip-limits` | **Date**: 2026-09-21 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Este documento desglosa todas las tareas de implementación organizadas por fases e historias de usuario (P1, P2, P3). Cada tarea incluye su **Definition of Done (DoD)** estricto: implementación de código limpio y su correspondiente prueba unitaria/integración en verde **sin usar `unittest.mock`** (inyectando repositorios falsos bajo DIP), cubriendo exhaustivamente los 7 casos de error y finalizando con la verificación de umbrales de cobertura constitucional.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialización del proyecto, configuración de dependencias, variables de entorno y utilidades base.

- [X] T001 Configure project dependencies in requirements.txt (FastAPI, SQLAlchemy, Alembic, Pydantic-Settings, PyJWT, passlib[bcrypt], bcrypt<4.1, email-validator, python-multipart, mcp, pytest, pytest-cov, pytest-asyncio, httpx)
- [X] T002 [P] Create environment template in .env.example with DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, and MCP_USER_EMAIL
- [X] T003 [P] Implement settings management in app/config.py using pydantic-settings to validate environment variables
- [X] T004 [P] Implement pure date normalization utilities in app/utils/date_utils.py without domain dependencies

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestructura central de base de datos, enums de dominio, excepciones de negocio y fakes de testing para DIP.

**⚠️ CRITICAL**: Ninguna historia de usuario puede iniciar hasta completar esta fase.

- [X] T005 Configure database engine, SessionLocal, and DeclarativeBase in app/database.py with SQLite conditional connect_args
- [X] T006 [P] Define domain enums PrioridadEnum ('baja', 'media', 'alta') and EstadoEnum ('pendiente', 'en_progreso', 'completada') in app/schemas/tarea.py
- [X] T007 [P] Define business exceptions (LimitePrioridadAltaExcedidoError, LimiteWIPExcedidoError, TransicionEstadoInvalidaError, RecursoAjenoError, RecursoNoEncontradoError) in app/services/exceptions.py
- [X] T008 [P] Implement in-memory fake repository FakeTareasRepository in tests/fakes/fake_tareas_repository.py for DIP testing without unittest.mock
- [X] T009 Configure test fixtures and in-memory SQLite database in tests/conftest.py with FastAPI TestClient and httpx.AsyncClient

**Checkpoint**: Base lista. Se puede iniciar la implementación de historias de usuario.

---

## Phase 3: User Story 1 - Registro y Autenticación de Usuario (Priority: P1) 🎯 MVP

**Goal**: Permitir el registro de usuarios con email único y contraseña hasheada (bcrypt<4.1), y login OAuth2 para obtener token JWT con expiración finita, sin exponer contraseñas.

**Independent Test**: Registrar usuario (201 sin password_hash en respuesta), rechazar email duplicado (400), obtener token JWT (200) y rechazar credenciales incorrectas (401).

### Tests for User Story 1
- [X] T010 [P] [US1] Create unit tests for password hashing and JWT token generation in tests/unit/test_auth_service.py without mocks
- [X] T011 [P] [US1] Create API integration tests for POST /usuarios/ and POST /usuarios/token in tests/api/test_auth_api.py covering duplicate email (400) and invalid credentials (401)

### Implementation for User Story 1
- [X] T012 [P] [US1] Implement Usuario SQLAlchemy model in app/models/usuario.py with unique index on email and non-nullable password_hash
- [X] T013 [P] [US1] Implement Pydantic DTOs UsuarioCreate, UsuarioOut, and TokenOut in app/schemas/usuario.py and app/schemas/token.py
- [X] T014 [US1] Implement UsuariosRepository in app/repositories/usuarios_repository.py for database queries (crear_usuario, obtener_por_email, obtener_por_id)
- [X] T015 [US1] Implement AuthService in app/services/auth_service.py with passlib[bcrypt] (bcrypt<4.1) and PyJWT HS256
- [X] T016 [US1] Implement get_current_user dependency in app/routers/deps.py decoding JWT Bearer token and retrieving authenticated user
- [X] T017 [US1] Implement authentication endpoints in app/routers/usuarios.py (POST /usuarios/ returning 201/400 and POST /usuarios/token returning 200/401)

**Checkpoint**: User Story 1 funcional y testable de forma independiente (MVP de autenticación).

---

## Phase 4: User Story 2 - Creación de Tareas y Control de Límite de Prioridad Alta (Priority: P1)

**Goal**: Permitir la creación de tareas personales validando que un usuario no pueda tener más de 2 tareas de prioridad alta abiertas simultáneamente.

**Independent Test**: Crear 2 tareas de prioridad 'alta' (201); verificar que una 3ra tarea de prioridad 'alta' abierta es rechazada con HTTP 400 LimitePrioridadAltaExcedidoError (Error Case 2); verificar que título vacío o prioridad inválida responde HTTP 422 (Error Case 1).

### Tests for User Story 2
- [X] T018 [P] [US2] Create unit tests with FakeTareasRepository in tests/unit/test_services_tareas.py verifying high-priority task limit and raising LimitePrioridadAltaExcedidoError on 3rd task without unittest.mock
- [X] T019 [P] [US2] Create API tests in tests/api/test_tareas_api.py for POST /tareas/ validating 201 creation, 400 LimitePrioridadAltaExcedidoError (Error Case 2), 401 without token (Error Case 5), and 422 on invalid schema (Error Case 1)

### Implementation for User Story 2
- [X] T020 [P] [US2] Implement Tarea SQLAlchemy model in app/models/tarea.py with foreign key usuario_id indexed and cascade delete
- [X] T021 [P] [US2] Implement Pydantic DTOs TareaCreate and TareaOut in app/schemas/tarea.py with strip_whitespace on titulo
- [X] T022 [US2] Implement task creation and high-priority count queries in app/repositories/tareas_repository.py strictly scoped by usuario_id
- [X] T023 [US2] Implement crear_tarea in app/services/tareas_service.py taking repo=tareas_repository default parameter (DIP) and validating high-priority limit <= 2
- [X] T024 [US2] Implement POST /tareas/ endpoint in app/routers/tareas.py delegating to service, obtaining usuario_id from get_current_user, and mapping LimitePrioridadAltaExcedidoError to HTTP 400

**Checkpoint**: User Story 2 funcional con validación de límite de prioridad alta e inyección DIP.

---

## Phase 5: User Story 3 - Gestión de Flujo de Trabajo y Límite WIP (Priority: P1)

**Goal**: Administrar transiciones de estado de tareas ('pendiente' -> 'en_progreso' -> 'completada') imponiendo un límite estricto de máximo 3 tareas en progreso simultáneamente.

**Independent Test**: Mover 3 tareas a 'en_progreso'; verificar que mover una 4ta tarea a 'en_progreso' es rechazado con 400 LimiteWIPExcedidoError (Error Case 3); verificar que saltar de 'pendiente' a 'completada' retorna 400 TransicionEstadoInvalidaError (Error Case 4).

### Tests for User Story 3
- [X] T025 [P] [US3] Create unit tests with FakeTareasRepository in tests/unit/test_services_tareas.py verifying WIP limit of 3 (Error Case 3) and invalid transitions (Error Case 4) without unittest.mock
- [X] T026 [P] [US3] Create API tests in tests/api/test_tareas_api.py for PATCH /tareas/{id}/estado validating 200, 400 LimiteWIPExcedidoError (Error Case 3), 400 TransicionEstadoInvalidaError (Error Case 4), 403 on another user's task (Error Case 6), and 404 on nonexistent task (Error Case 7)

### Implementation for User Story 3
- [X] T027 [P] [US3] Implement Pydantic DTO TareaUpdateEstado in app/schemas/tarea.py with EstadoEnum validation
- [X] T028 [US3] Implement contar_por_estado and actualizar_estado in app/repositories/tareas_repository.py filtered by usuario_id
- [X] T029 [US3] Implement cambiar_estado_tarea in app/services/tareas_service.py with repo=tareas_repository (DIP) enforcing state machine rules and WIP limit <= 3
- [X] T030 [US3] Implement PATCH /tareas/{id}/estado endpoint in app/routers/tareas.py translating business exceptions to HTTP 400, 403, and 404

**Checkpoint**: User Stories 1, 2 y 3 funcionales con todas las reglas de negocio críticas implementadas.

---

## Phase 6: User Story 4 - Consulta, Filtrado y Aislamiento de Tareas (Priority: P2)

**Goal**: Permitir listar tareas con paginación (skip/limit, orden descendente por fecha/id por defecto) y filtros (estado, prioridad), y consultar una tarea por ID con aislamiento multi-inquilino estricto.

**Independent Test**: Consultar listado y verificar paginación y orden descendente; verificar que usuario A no puede ver tareas de usuario B (403 Forbidden, Error Case 6); verificar que ID inexistente retorna 404 (Error Case 7); verificar que sin token retorna 401 (Error Case 5).

### Tests for User Story 4
- [X] T031 [P] [US4] Create unit tests with FakeTareasRepository in tests/unit/test_services_tareas.py verifying task querying, pagination, and ownership enforcement without unittest.mock
- [X] T032 [P] [US4] Create API tests in tests/api/test_tareas_api.py for GET /tareas/ and GET /tareas/{id} verifying 200, 401 (Error Case 5), 403 (Error Case 6), and 404 (Error Case 7)

### Implementation for User Story 4
- [X] T033 [US4] Implement listar_tareas (with skip, limit, filters, and ORDER BY creado_en DESC, id DESC) and obtener_por_id in app/repositories/tareas_repository.py
- [X] T034 [US4] Implement listar_tareas and obtener_tarea_por_id in app/services/tareas_service.py enforcing usuario_id matching and raising RecursoAjenoError / RecursoNoEncontradoError
- [X] T035 [US4] Implement GET /tareas/ and GET /tareas/{id} endpoints in app/routers/tareas.py with query parameters skip, limit, estado, and prioridad

**Checkpoint**: Consultas y aislamiento por usuario totalmente operativos.

---

## Phase 7: User Story 5 - Eliminación Segura de Tareas (Priority: P3)

**Goal**: Permitir a los usuarios eliminar sus propias tareas permanentemente (204 No Content), impidiendo eliminar tareas de otros usuarios (403) o inexistentes (404).

**Independent Test**: Eliminar tarea propia (204) y verificar que ya no existe; verificar que intentar eliminar tarea de otro usuario devuelve 403 (Error Case 6); verificar que ID inexistente devuelve 404 (Error Case 7).

### Tests for User Story 5
- [X] T036 [P] [US5] Create unit tests with FakeTareasRepository in tests/unit/test_services_tareas.py verifying deletion, ownership check (Error Case 6), and nonexistent task check (Error Case 7) without unittest.mock
- [X] T037 [P] [US5] Create API tests in tests/api/test_tareas_api.py for DELETE /tareas/{id} verifying 204 No Content, 403 Forbidden (Error Case 6), and 404 Not Found (Error Case 7)

### Implementation for User Story 5
- [X] T038 [US5] Implement eliminar_tarea in app/repositories/tareas_repository.py strictly scoped by usuario_id and returning deletion success
- [X] T039 [US5] Implement eliminar_tarea in app/services/tareas_service.py with repo=tareas_repository (DIP) verifying ownership
- [X] T040 [US5] Implement DELETE /tareas/{id} endpoint in app/routers/tareas.py returning HTTP 204 No Content or mapping to 403/404

**Checkpoint**: CRUD REST completo y protegido contra vulnerabilidades IDOR.

---

## Phase 8: User Story 6 - Asistencia Automatizada mediante MCP (Priority: P2)

**Goal**: Exponer las herramientas MCP (crear_tarea, listar_tareas, iniciar_tarea_prioritaria) reutilizando app/services/tareas_service.py, retornando errores estructurados {"error": "..."} y resolviendo la identidad del usuario vía MCP_USER_EMAIL en transporte stdio.

**Independent Test**: Invocar crear_tarea vía MCP validando límite de prioridad alta; invocar listar_tareas; invocar iniciar_tarea_prioritaria verificando que avanza la tarea pendiente con mayor prioridad respetando el límite WIP de 3 con errores {"error": "..."}; verificar transporte stdio con fallback a MCP_USER_EMAIL.

### Tests for User Story 6
- [X] T041 [P] [US6] Create integration tests in tests/api/test_mcp_api.py verifying MCP tool invocations, priority ordering in iniciar_tarea_prioritaria, and structured error responses {"error": "..."}

### Implementation for User Story 6
- [X] T042 [US6] Implement iniciar_tarea_prioritaria in app/services/tareas_service.py selecting highest priority pending task and moving to en_progreso under WIP limit with repo=tareas_repository (DIP)
- [X] T043 [US6] Implement MCP tools (crear_tarea, listar_tareas, iniciar_tarea_prioritaria) in app/mcp/tools.py delegating to services/tareas_service.py and formatting business errors as {"error": "..."}
- [X] T044 [US6] Implement MCP server setup and stdio CLI entrypoint in app/mcp/server.py resolving user identity from MCP_USER_EMAIL with documented fallback
- [X] T045 [US6] Assemble FastAPI application and mount routers and MCP server in app/main.py with global 500 error handler returning {"detail": "Error interno del servidor"}

**Checkpoint**: Interfaz agéntica MCP y API REST totalmente sincronizadas y operativas.

---

## Phase 9: Polish, Quality Gates & Coverage Verification

**Purpose**: Verificación de migraciones Alembic, validación de inicio rápido y aseguramiento estricto de cobertura constitucional.

- [X] T046 [P] Configure Alembic migrations environment in alembic/ and alembic.ini, and generate initial migration script in alembic/versions/ for usuarios and tareas tables
- [X] T047 Execute full end-to-end verification script following quickstart.md scenarios validating REST API and MCP flows
- [X] T048 Verify test suite passes and constitutional coverage thresholds are met (services/ >= 90%, global combined >= 70% omitting main.py, mcp/*, logging_config.py) using pytest --cov=app --cov-report=term-missing --cov-fail-under=70

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: Sin dependencias, inicia de inmediato.
- **Foundational (Phase 2)**: Depende de Phase 1. Bloquea todas las historias de usuario.
- **User Stories (Phase 3+)**: Dependen de Phase 2 completada.
  - US1 (Autenticación) es el prerrequisito de seguridad para los endpoints protegidos.
  - US2 (Creación) y US3 (WIP/Transiciones) construyen el núcleo de dominio de tareas.
  - US4 (Lectura) y US5 (Eliminación) completan el ciclo de vida.
  - US6 (MCP) reutiliza los servicios construidos en US2, US3 y US4.
- **Polish & Coverage (Phase 9)**: Depende de todas las fases anteriores completas.

### Mapeo Explícito de Casos de Error de spec.md
1. **Caso 1 (Crear tarea con título vacío o prioridad inválida -> 422)**: Cubierto en T019, T021, T024.
2. **Caso 2 (Crear 3ra tarea de prioridad alta con 2 abiertas -> 400 LimitePrioridadAltaExcedidoError)**: Cubierto en T018, T019, T023, T024.
3. **Caso 3 (Mover 4ta tarea a en_progreso con 3 en progreso -> 400 LimiteWIPExcedidoError)**: Cubierto en T025, T026, T029, T030.
4. **Caso 4 (Pasar de pendiente a completada sin en_progreso -> 400 TransicionEstadoInvalidaError)**: Cubierto en T025, T026, T029, T030.
5. **Caso 5 (Listar o crear tareas sin token -> 401 Unauthorized)**: Cubierto en T019, T032.
6. **Caso 6 (Modificar o eliminar tarea de otro usuario -> 403 Forbidden)**: Cubierto en T026, T032, T037.
7. **Caso 7 (Modificar o eliminar tarea inexistente -> 404 Not Found)**: Cubierto en T026, T032, T037.

---

## Parallel Execution Opportunities

- En **Phase 1**: T002, T003 y T004 pueden ejecutarse en paralelo.
- En **Phase 2**: T006, T007 y T008 pueden ejecutarse en paralelo.
- En **User Story 1**: T010, T011, T012 y T013 pueden ejecutarse en paralelo antes de T014-T017.
- En **User Story 2**: T018, T019, T020 y T021 pueden ejecutarse en paralelo antes de T022-T024.
- En **User Story 3**: T025, T026 y T027 pueden ejecutarse en paralelo antes de T028-T030.
- En **User Story 4**: T031 y T032 pueden ejecutarse en paralelo antes de T033-T035.
- En **User Story 5**: T036 y T037 pueden ejecutarse en paralelo antes de T038-T040.

---

## Implementation Strategy (MVP First)

1. **Paso 1**: Completar Phase 1 (Setup) y Phase 2 (Foundational).
2. **Paso 2**: Implementar Phase 3 (User Story 1 - Registro y Login). **Validar MVP de Autenticación**.
3. **Paso 3**: Implementar Phase 4 (User Story 2 - Creación y Límite de Prioridad Alta).
4. **Paso 4**: Implementar Phase 5 (User Story 3 - Límite WIP y Transiciones).
5. **Paso 5**: Implementar Phase 6 y 7 (User Stories 4 y 5 - Consulta y Eliminación).
6. **Paso 6**: Implementar Phase 8 (User Story 6 - MCP Tools).
7. **Paso 7**: Completar Phase 9 (Alembic y validación de umbrales de cobertura $\ge 90\%$ services, $\ge 70\%$ global).
