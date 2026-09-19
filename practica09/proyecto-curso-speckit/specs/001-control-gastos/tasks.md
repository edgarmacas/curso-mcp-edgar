# Tasks: Sistema de Control de Gastos Personales

**Feature**: Sistema de Control de Gastos Personales  
**Branch**: `001-control-gastos`  
**Specification**: [specs/001-control-gastos/spec.md](spec.md)  
**Implementation Plan**: [specs/001-control-gastos/plan.md](plan.md)  

---

## Definition of Done (DoD) Obligatoria para Tareas de Implementación
Para que cualquier tarea de implementación se considere completada, DEBE cumplir con:
1. **Código escrito**: Implementación limpia, tipada y modular en el archivo correspondiente.
2. **Test en verde**: Prueba unitaria, de integración o de API escrita y ejecutada exitosamente (`pytest` en verde).
3. **Cumplimiento constitucional**: No violar ningún artículo de la Constitución v1.0.0 (respetar capas, DIP sin mocks frágiles, seguridad JWT, filtros `usuario_id` y compatibilidad Sesiones 6-8).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialización del proyecto, dependencias y estructura de paquetes compartidos.

- [X] T001 Crear la estructura completa de paquetes Python bajo `app/` (`models/`, `schemas/`, `repositories/`, `services/`, `routers/`, `utils/`, `mcp/`) y directorios de pruebas (`tests/unit/`, `tests/integration/`, `tests/api/`) con sus respectivos archivos `__init__.py`
- [X] T002 Crear archivo de dependencias `requirements.txt` fijando `fastapi`, `uvicorn[standard]`, `sqlalchemy>=2.0`, `alembic`, `pyjwt`, `passlib[bcrypt]`, `bcrypt>=4.0.1,<4.1.0`, `pydantic-settings`, `email-validator`, `python-multipart`, `mcp`, `pytest`, `pytest-cov`, `httpx`
- [X] T003 [P] Crear plantilla de variables de entorno `.env.example` y módulo de configuración tipada en `app/config.py` utilizando `pydantic_settings.BaseSettings` para leer `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `DATABASE_URL` y `DEMO_USER_EMAIL`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestructura transversal crítica que bloquea la implementación de historias de usuario.

- [X] T004 Implementar configuración de base de datos agnóstica (SQLite/PostgreSQL) en `app/database.py` con `create_engine`, `SessionLocal`, `Base = declarative_base()` y generador `get_db` aplicando `connect_args` condicional para SQLite (Artículo III.2)
- [X] T005 [P] Configurar entorno de migraciones con Alembic inicializando `alembic.ini` y `alembic/env.py` vinculado a `app.database.Base.metadata`
- [X] T006 [P] Implementar funciones puras de seguridad en `app/utils/security.py` para hashing (`passlib` con `bcrypt<4.1`), verificación de contraseñas, generación y decodificación de tokens JWT HS256 (`pyjwt`) (Artículo IV.1, IV.2, I.4)
- [X] T007 Implementar aplicación principal FastAPI en `app/main.py` con manejador global de excepciones no controladas retornando HTTP 500 con `{"detail": "Error interno del servidor"}` (Artículo IV.5)
- [X] T008 [P] Configurar fixtures compartidas de pytest en `tests/conftest.py` y `tests/__init__.py` para motor SQLite en memoria (`sqlite:///:memory:`), sesión de pruebas, cliente HTTP (`httpx.AsyncClient` / `TestClient`) y tokens auxiliares (Artículo VII.4, VIII.1)

---

## Phase 3: User Story 1 - Registro y Autenticación de Usuarios (Priority: P1) 🎯 MVP

**Goal**: Permitir a los usuarios registrarse de forma segura con email único y contraseña, e iniciar sesión mediante OAuth2 Password Flow para recibir un token JWT.

**Independent Test**: Registrar cuenta vía `POST /usuarios/` (verificando que no retorne password y rechace emails duplicados con 400), e iniciar sesión vía `POST /usuarios/token` (verificando retorno de JWT con 200 y rechazo de credenciales erróneas con 401).

- [X] T009 [P] [US1] Crear modelo SQLAlchemy `Usuario` en `app/models/usuario.py` con campos `id`, `email` (único, indexado), `hashed_password` y `fecha_creacion`. DoD: código escrito, test en verde en `tests/integration/test_repo_usuarios.py`, cumple Art. III y IV
- [X] T010 [P] [US1] Crear esquemas Pydantic en `app/schemas/usuario.py` (`UsuarioCreate`, `UsuarioOut` con `ConfigDict(from_attributes=True)` excluyendo contraseña, y `Token`). DoD: código escrito, validaciones unitarias en verde, cumple Art. IV.6 y V.3
- [X] T011 [US1] Implementar funciones de persistencia de usuario `obtener_por_email(db, email) -> Usuario | None` y `guardar(db, email, hashed_password) -> Usuario` en `app/repositories/usuarios.py` (módulo funcional, no clase). DoD: código escrito, pruebas de integración en `tests/integration/test_repo_usuarios.py` en verde con SQLite en memoria, cumple Art. I.3 y VIII.2
- [X] T012 [US1] Implementar lógica de negocio de usuarios en `app/services/auth.py` con funciones `registrar_usuario(db, email, password, repo=usuarios_repository)` y `autenticar_usuario(db, email, password, repo=usuarios_repository)`. DoD: código escrito, tests unitarios en `tests/unit/test_services_auth.py` inyectando repositorio falso en verde sin `unittest.mock`, cumple Art. I.2, II.1, II.3 y IV
- [X] T013 [US1] Implementar dependencia de autenticación `get_current_user` en `app/dependencies.py` para decodificar JWT, validar firma y cargar entidad usuario. DoD: código escrito, tests unitarios de extracción de identidad en verde, cumple Art. IV.4
- [X] T014 [US1] Implementar endpoints REST `POST /usuarios/` (201 Created / 400 email duplicado / 422) y `POST /usuarios/token` (200 OK con JWT / 401 credenciales inválidas) en `app/routers/usuarios.py`. DoD: código escrito, tests de API en `tests/api/test_api_usuarios.py` en verde, cumple Art. I.1, V.1

---

## Phase 4: User Story 2 - Registro de Gastos con Límite de Categoría (Priority: P1)

**Goal**: Permitir a usuarios autenticados registrar gastos con descripción, monto positivo y categoría válida, rechazando operaciones que hagan que el acumulado de la categoría supere 500.0.

**Independent Test**: Registrar gasto vía `POST /gastos/`; verificar 201 en caso válido, 400 ante categoría inválida (`CategoriaInvalidaError`), 400 ante límite de 500.0 excedido (`LimiteExcedidoError`), y 422 ante monto $\le 0$ o descripción vacía.

- [X] T015 [P] [US2] Crear modelo SQLAlchemy `Gasto` en `app/models/gasto.py` con campos `id`, `usuario_id` (FK `usuarios.id`, indexado), `descripcion`, `monto`, `categoria` y `fecha`. DoD: código escrito, test de relaciones en `tests/integration/test_repo_gastos.py` en verde, cumple Art. III.3
- [X] T016 [P] [US2] Crear esquemas Pydantic en `app/schemas/gasto.py` (`GastoCreate` con validaciones `monto > 0` y `descripcion` no vacía, y `GastoOut` con `ConfigDict(from_attributes=True)`). DoD: código escrito, tests de validación en verde, cumple Art. IV.6 y V.3
- [X] T017 [US2] Implementar funciones de repositorio `guardar(db, usuario_id, descripcion, monto, categoria) -> dict` y `total_por_categoria(db, usuario_id, categoria) -> float` en `app/repositories/gastos.py` (módulo funcional devolviendo dict/float, nunca objetos ORM). DoD: código escrito, tests de integración en `tests/integration/test_repo_gastos.py` en verde con SQLite en memoria, cumple Art. I.3 y VIII.2
- [X] T018 [US2] Implementar en `app/services/gastos.py`: excepciones `CategoriaInvalidaError` y `LimiteExcedidoError`, constante `LIMITE_POR_CATEGORIA = 500.0`, y función `registrar_gasto(db, usuario_id, descripcion, monto, categoria, repo=gastos_repository) -> dict` con validación separada (`_validar_gasto`). Cubrir **Caso de Error 1** (monto $\le 0$), **Caso de Error 2** (categoría inexistente) y **Caso de Error 3** (límite acumulado > 500.0). DoD: código escrito, tests unitarios en `tests/unit/test_services_gastos.py` inyectando `RepositorioFalso` en verde sin `unittest.mock`, cumple Art. I.2, II.1, II.2, II.3 y VIII.1
- [X] T019 [US2] Implementar proveedor de repositorio `get_gastos_repo` en `app/dependencies.py` para inyección en endpoints. DoD: código escrito, test en verde, cumple Art. II.3
- [X] T020 [US2] Implementar endpoint REST `POST /gastos/` en `app/routers/gastos.py` inyectando `usuario_id` exclusivamente desde `get_current_user`. DoD: código escrito, tests de API en `tests/api/test_api_gastos.py` en verde cubriendo éxito (201) y errores (400 categoría, 400 límite, 422 monto/descripción), cumple Art. I.1, IV.4, V.1

---

## Phase 5: User Story 3 - Listado Paginado de Gastos Personales (Priority: P2)

**Goal**: Permitir a usuarios autenticados consultar sus gastos registrados con parámetros de paginación (`skip`, `limit`).

**Independent Test**: Consultar `GET /gastos/?skip=0&limit=20` con token válido; verificar listado ordenado y tamaño de página, y respuesta 422 ante `skip < 0` o `limit < 1`.

- [X] T021 [US3] Implementar función de repositorio `listar(db, usuario_id, skip=0, limit=20) -> list[dict]` en `app/repositories/gastos.py` aplicando filtro obligatorio por `usuario_id` y orden descendente por fecha. DoD: código escrito, tests de integración en `tests/integration/test_repo_gastos.py` en verde, cumple Art. I.3, III.3 y VIII.2
- [X] T022 [US3] Implementar función de servicio `listar_gastos(db, usuario_id, skip=0, limit=20, repo=gastos_repository) -> list[dict]` en `app/services/gastos.py` con firma posicional y keyword default. DoD: código escrito, tests unitarios en `tests/unit/test_services_gastos.py` con `RepositorioFalso` en verde, cumple Art. I.2, II.3 y VIII.1
- [X] T023 [US3] Implementar endpoint REST `GET /gastos/` en `app/routers/gastos.py` con query params validados `skip` y `limit`, obteniendo `usuario_id` desde `get_current_user`. DoD: código escrito, tests de API en `tests/api/test_api_gastos.py` en verde (verificando 200 OK y 422 en parámetros inválidos), cumple Art. I.1, IV.4, V.1, V.2

---

## Phase 6: User Story 4 - Aislamiento Multitenant y Seguridad Estricta (Priority: P1)

**Goal**: Garantizar la total privacidad de los gastos, impidiendo accesos cruzados entre usuarios, ignorando cualquier identificador externo provisto manualmente y rechazando peticiones sin autenticación.

**Independent Test**: Ejecutar suite de pruebas de seguridad: peticiones sin token retornan 401; peticiones con ID de otro usuario en query params o body son ignoradas y operan solo sobre el usuario autenticado.

- [X] T024 [US4] Implementar suite de pruebas de aislamiento en `tests/api/test_api_gastos_isolation.py` cubriendo:
  - **Caso de Error 4**: Peticiones a `POST /gastos/` y `GET /gastos/` sin header Authorization retornan HTTP 401 Unauthorized.
  - **Caso de Error 5**: Intentos de consultar gastos pasando manualmente `?usuario_id=99` o `{"usuario_id": 99}` son ignorados, verificando que jamás se filtre por ese ID y solo se retornen gastos del token autenticado.
  - **Aislamiento de límites**: Verificar que el acumulado de 490.0 en comida de un Usuario A no bloquea a un Usuario B con 0.0 en comida para registrar un gasto de 80.0.
  DoD: tests escritos y fallando inicialmente hasta verificar robustez total, cumple Art. IV.4, V.1
- [X] T025 [US4] Auditar y reforzar `app/routers/gastos.py` y `app/dependencies.py` para asegurar que ningún esquema ni endpoint exponga o acepte `usuario_id` como parámetro de entrada del cliente. DoD: código verificado, tests de `test_api_gastos_isolation.py` en verde, cumple Art. IV.4

---

## Phase 7: User Story 5 - Integración de Asistente MCP (Priority: P2)

**Goal**: Exponer herramientas de agente `registrar_gasto` y `listar_gastos` bajo el protocolo MCP en la misma app FastAPI vía streamable-http, delegando directamente a `services/gastos.py` y formateando errores como `{"error": "..."}`.

**Independent Test**: Invocar herramientas MCP mediante cliente o sesión streamable-http/stdio; verificar creación de gasto, listado, resolución de identidad desde el token y captura de errores estructurados.

- [X] T026 [US5] Implementar herramientas MCP `registrar_gasto(descripcion, monto, categoria)` y `listar_gastos(skip=0, limit=20)` en `app/mcp/server.py` delegando a `app.services.gastos` y capturando `CategoriaInvalidaError`, `LimiteExcedidoError` y excepciones de validación para retornar `{"error": str(e)}` (Artículo VI.1, VI.2, VI.3)
- [X] T027 [US5] Montar endpoint MCP streamable-http sobre FastAPI en `app/main.py` extrayendo el token JWT del header `Authorization` de la sesión MCP, con fallback documentado a `DEMO_USER_EMAIL` en `.env` para transporte `stdio` (Artículo VI.4)
- [X] T028 [US5] Implementar tests de MCP en `tests/api/test_mcp_tools.py` cubriendo al menos dos tests por tool:
  - `registrar_gasto`: (1) éxito registrando gasto para usuario autenticado, (2) retorno estructurado `{"error": "..."}` ante categoría inválida o límite excedido.
  - `listar_gastos`: (1) éxito listando gastos paginados, (2) manejo de parámetros inválidos.
  DoD: código escrito, tests de MCP en verde, cumple Art. VI y VII.6

---

## Phase 8: Compatibilidad con el Proyecto de Referencia (Sesiones 6-8)

**Purpose**: Asegurar compatibilidad inmutable y retroactiva con los contratos fijados en el proyecto original de las Sesiones 6-8.

- [X] T029 Integrar y ejecutar suite de pruebas de referencia `tests/test_gastos.py` conteniendo la clase `RepositorioFalso` y validando las firmas exactas de `registrar_gasto`, `listar_gastos`, `CategoriaInvalidaError`, `LimiteExcedidoError` y `LIMITE_POR_CATEGORIA = 500.0`. DoD: tests de `test_gastos.py` ejecutados sin modificaciones y pasando en verde al 100%, cumple Art. VIII.1
- [X] T030 Integrar y ejecutar suite de pruebas de referencia `tests/test_api_gastos.py` verificando el import `from tests.test_gastos import RepositorioFalso` y el uso de `app.dependency_overrides`. DoD: tests de `test_api_gastos.py` ejecutados sin modificaciones y pasando en verde al 100%, cumple Art. VII.5, VIII.1

---

## Phase 9: Pulido, Validación E2E y Puerta de Cobertura Final

**Purpose**: Verificación de migraciones, validación integral y comprobación obligatoria de los umbrales constitucionales de cobertura.

- [X] T031 [P] Generar migración inicial de base de datos en `alembic/versions/` para las tablas `usuarios` y `gastos` y documentar comando de aplicación en `README.md`
- [X] T032 Ejecutar los escenarios de validación manual descritos en `specs/001-control-gastos/quickstart.md` verificando el flujo E2E completo vía HTTP con `curl`
- [X] T033 Ejecutar exclusivamente `pytest --cov=app --cov-report=term-missing` y verificar rigurosamente los umbrales de cobertura del Artículo VII.3 de la Constitución:
  - 100% de reglas de negocio de `spec.md` cubiertas.
  - Cobertura de `app/services/` $\ge 90\%$.
  - Cobertura global combinada (`services + repositories + routers + utils`) $\ge 80\%$.
  - Exclusión confirmada de `main.py`, `mcp/*` y `logging_config.py` en el reporte.
  DoD: reporte generado sin fallos y con todos los umbrales superados.

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Setup)**: Sin dependencias, inicia de inmediato.
- **Phase 2 (Foundational)**: Depende de Phase 1. Bloquea todas las historias de usuario.
- **Phase 3 (User Story 1 - Auth)**: Depende de Phase 2. Establece el modelo `Usuario` y la autenticación JWT (MVP).
- **Phase 4 (User Story 2 - Gastos)**: Depende de Phase 2 y Phase 3 (requiere `Usuario` para FK y `get_current_user`).
- **Phase 5 (User Story 3 - Listado)**: Depende de Phase 4 (utiliza `Gasto` y repositorio de gastos).
- **Phase 6 (User Story 4 - Aislamiento)**: Depende de Phase 4 y Phase 5.
- **Phase 7 (User Story 5 - MCP)**: Depende de Phase 4 y Phase 5 (reutiliza `services/gastos.py`).
- **Phase 8 (Compatibilidad Sesiones 6-8)**: Depende de Phase 4 y Phase 5.
- **Phase 9 (Pulido y Cobertura Final)**: Depende de todas las fases anteriores.

### Matriz de Cobertura de Casos de Error del Spec
| Caso de Error del Spec | Tarea(s) de Implementación y Test | Archivos Involucrados |
|------------------------|-----------------------------------|-----------------------|
| 1. Monto negativo o cero | T016, T018, T020 | `app/schemas/gasto.py`, `app/services/gastos.py`, `tests/unit/test_services_gastos.py` |
| 2. Categoría inexistente | T018, T020 | `app/services/gastos.py`, `app/routers/gastos.py`, `tests/unit/test_services_gastos.py` |
| 3. Límite acumulado > 500.0 | T018, T020 | `app/services/gastos.py`, `tests/unit/test_services_gastos.py`, `tests/api/test_api_gastos.py` |
| 4. Sin token -> 401 | T020, T023, T024 | `app/dependencies.py`, `tests/api/test_api_gastos_isolation.py` |
| 5. ID ajeno manual ignorado | T024, T025 | `app/routers/gastos.py`, `tests/api/test_api_gastos_isolation.py` |

---

## Parallel Opportunities

- **Setup**: T002 y T003 pueden ejecutarse en paralelo tras T001.
- **Foundational**: T005, T006 y T008 pueden ejecutarse en paralelo tras T004.
- **User Story 1**: T009 (`Usuario` model) y T010 (`Usuario` schemas) pueden ejecutarse en paralelo.
- **User Story 2**: T015 (`Gasto` model) y T016 (`Gasto` schemas) pueden ejecutarse en paralelo.
- **MCP & Compatibilidad**: Tras completar User Story 2 y 3, Phase 7 (MCP) y Phase 8 (Compatibilidad Sesiones 6-8) pueden ejecutarse en paralelo.
