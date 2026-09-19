# Feature Specification: Sistema de Control de Gastos Personales

**Feature Branch**: `001-control-gastos`

**Created**: 2026-09-19

**Status**: Draft

**Input**: User description: "Sistema de control de gastos personales. Entidades: Usuario: email (único), contraseña (nunca expuesta en respuestas). Gasto: descripción, monto (> 0), categoría, pertenece a un usuario. Reglas de negocio: Categorías válidas: comida, transporte, entretenimiento, otros. Cualquier otra categoría es un error de negocio, no una excepción genérica. El monto de un gasto debe ser mayor a cero; una descripción vacía también es inválida. Un gasto no puede hacer que el total acumulado de su categoría supere 500. Un usuario solo puede ver y crear gastos propios; nunca los de otro usuario, sin importar qué identificador se pase en la solicitud. Contrato de la API (REST): POST /usuarios/ (201 Usuario, 400 email duplicado, 422), POST /usuarios/token (200 token JWT, 401), POST /gastos/ (201 Gasto, 400 categoría inválida, 400 límite excedido, 401, 422), GET /gastos/ (200 lista, 401, 422). Contrato equivalente por MCP: Tool registrar_gasto, Tool listar_gastos con usuario autenticado. Contrato de compatibilidad (no negociable): Sesiones 6-8 firmas fijas e inmutables. Casos de error explícitos que deben tener test: monto negativo/cero, categoría inexistente, límite 500 excedido, sin token -> 401, listar pasando ID ajeno ignorado."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration & Authentication (Priority: P1)

As a new or returning user, I want to register securely with an email and password and authenticate to receive an access token, so that I can safely manage my private expenses.

**Why this priority**: It is the foundation for identity, privacy, and security in a multi-user system. Without authentication, private expense tracking cannot function.

**Independent Test**: Can be fully tested by registering a new account, verifying that passwords are never returned in responses, and using credentials to obtain a valid access token.

**Acceptance Scenarios**:

1. **Given** a new user with a unique email and valid password, **When** submitting registration to `/usuarios/`, **Then** the account is created with status 201 and credentials/passwords are excluded from the response.
2. **Given** an existing registered email, **When** another user attempts registration with that same email, **Then** the system rejects registration with HTTP status 400 indicating duplicate email.
3. **Given** an existing account, **When** logging in via `/usuarios/token` with valid credentials, **Then** an access token is returned with status 200.
4. **Given** incorrect credentials (wrong password or unregistered email), **When** attempting login via `/usuarios/token`, **Then** access is denied with HTTP status 401.

---

### User Story 2 - Record Personal Expense with Category Limits (Priority: P1)

As an authenticated user, I want to record an expense with a non-empty description, a positive amount, and a valid category, so that I can track my spending while preventing cumulative totals from exceeding 500 per category.

**Why this priority**: Core value proposition and business logic of the expense control system.

**Independent Test**: Can be fully tested by submitting expenses under different categories and amounts, verifying rejection of invalid categories, non-positive amounts, and transactions exceeding the category ceiling of 500.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** submitting a new expense with valid description ("Almuerzo"), amount (45.0), and category ("comida"), **Then** the expense is recorded, associated with the user, and returned with status 201.
2. **Given** an authenticated user, **When** submitting an expense with an invalid category (e.g., "viajes"), **Then** the request is rejected with HTTP 400 and a specific business error (`CategoriaInvalidaError`).
3. **Given** an authenticated user, **When** submitting an expense with amount <= 0 (e.g., 0.0 or -15.0) or an empty description, **Then** the request is rejected with validation error status (400 or 422).
4. **Given** an authenticated user with an accumulated total of 450.0 in "transporte", **When** attempting to record a new expense of 60.0 in "transporte" (which would reach 510.0), **Then** the request is rejected with HTTP 400 and a specific business error (`LimiteExcedidoError`).
5. **Given** an authenticated user with an accumulated total of 450.0 in "entretenimiento", **When** recording a new expense of 50.0 in "entretenimiento" (reaching exactly 500.0), **Then** the expense is accepted, saved, and returned with status 201.

---

### User Story 3 - List and Paginate Personal Expenses (Priority: P2)

As an authenticated user, I want to retrieve a paginated list of my recorded expenses, so that I can review my transaction history in controlled page sizes.

**Why this priority**: Essential for reviewing history and viewing personal records without loading entire data sets at once.

**Independent Test**: Can be fully tested by registering multiple expenses for a user and querying `/gastos/` with `skip` and `limit` parameters to confirm expected ordering and batch boundaries.

**Acceptance Scenarios**:

1. **Given** an authenticated user with recorded expenses, **When** querying `/gastos/` without query parameters, **Then** the system returns the first page of expenses (up to default limit 20) with status 200.
2. **Given** an authenticated user with 25 expenses, **When** querying `/gastos/?skip=10&limit=10`, **Then** exactly 10 expenses representing records 11 through 20 are returned with status 200.
3. **Given** an authenticated user, **When** querying `/gastos/` with invalid pagination parameters (e.g., negative skip or limit < 1), **Then** the request fails with status 422.

---

### User Story 4 - Multi-User Isolation & Privacy Enforcement (Priority: P1)

As an authenticated user, I want complete data confidentiality such that my expenses are strictly private and inaccessible to any other user under any circumstances.

**Why this priority**: Fundamental security and privacy guarantee; strictly mandated by project constitution and core user requirements.

**Independent Test**: Can be fully tested by creating two separate users (User A and User B), recording expenses for both, and verifying that queries by User A never return User B's expenses, and that User A supplying User B's ID in request parameters is completely ignored.

**Acceptance Scenarios**:

1. **Given** User A and User B each have recorded expenses, **When** User A lists expenses via `/gastos/`, **Then** only User A's expenses are returned; User B's records are never visible.
2. **Given** User A is authenticated, **When** User A passes User B's identifier in query parameters or payload, **Then** the system ignores the parameter, resolves identity exclusively from User A's authentication token, and returns/modifies only User A's data.
3. **Given** User A has accumulated 490.0 in "comida", **When** User B (with 0.0 in "comida") records an expense of 80.0 in "comida", **Then** User B's expense is accepted (User A's accumulated total does not impact User B).
4. **Given** an unauthenticated request to `/gastos/` (missing or invalid token), **When** attempting to list or create expenses, **Then** access is denied with status 401.

---

### User Story 5 - Assistant & AI Agent Integration via MCP (Priority: P2)

As a user or conversational AI client operating via the Model Context Protocol (MCP), I want to record and list personal expenses through structured tools (`registrar_gasto`, `listar_gastos`), so that I can manage my budget using natural language assistants with identical business rules.

**Why this priority**: Enables automated, agentic, and voice/chat workflows while keeping business logic and security unified across interfaces.

**Independent Test**: Can be fully tested by invoking MCP tools `registrar_gasto` and `listar_gastos` from an MCP client session and verifying that business errors, identity bindings, and category limits behave identically to the REST API.

**Acceptance Scenarios**:

1. **Given** an authenticated MCP session, **When** calling `registrar_gasto(descripcion, monto, categoria)` with valid arguments, **Then** the expense is registered for the authenticated user and returned as a structured entity.
2. **Given** an authenticated MCP session, **When** calling `registrar_gasto` with an invalid category or an amount exceeding 500, **Then** the tool returns a structured error object `{"error": "..."}` rather than raising an unhandled exception.
3. **Given** an authenticated MCP session, **When** calling `listar_gastos(skip=0, limit=20)`, **Then** the user's personal expenses are returned as a structured list.
4. **Given** an MCP session, **When** tools are invoked, **Then** user identity is bound to the verified session token (or documented demo user in stdio fallback mode) and cannot be overridden by tool parameters.

---

### Edge Cases

- **Empty or Whitespace-Only Description**: An expense with description `""` or `"   "` must be rejected as invalid input.
- **Float Boundary at 500.0**: An accumulated total of 499.99 plus an expense of 0.01 reaches exactly 500.00 and is allowed; an expense of 0.02 reaches 500.01 and is rejected with `LimiteExcedidoError`.
- **Case Sensitivity in Categories**: Categories are strictly lowercase: `comida`, `transporte`, `entretenimiento`, `otros`. Inputs such as `Comida` or `OTROS` must be rejected with `CategoriaInvalidaError` unless normalized before service entry.
- **Empty Result Pages**: When `skip` exceeds the total number of records for a user, the response is an empty list `[]` with HTTP status 200 (not an error).
- **Token Expiration**: Requests presenting an expired JWT token must be rejected with HTTP 401.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow users to register an account by providing an email and a password.
- **FR-002**: The system MUST reject registration if the email is already registered, returning an explicit HTTP 400 error.
- **FR-003**: The system MUST store passwords hashed using `passlib[bcrypt]` and MUST NEVER return or log plaintext passwords or password hashes in any response.
- **FR-004**: The system MUST authenticate users via OAuth2 Password Flow and issue an HS256-signed JWT token with configurable expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- **FR-005**: The system MUST protect all expense endpoints (`/gastos/`) and MCP tools, requiring valid authentication and returning HTTP 401 when the token is missing or invalid.
- **FR-006**: The system MUST allow authenticated users to record an expense specifying description, amount, and category.
- **FR-007**: The system MUST validate that the expense amount is strictly greater than zero (`monto > 0`) and that the description is non-empty.
- **FR-008**: The system MUST restrict expense categories exclusively to: `comida`, `transporte`, `entretenimiento`, `otros`. Any other category MUST be rejected with a business error (`CategoriaInvalidaError`, HTTP 400).
- **FR-009**: The system MUST maintain and check the accumulated total per user and category, rejecting any expense that would cause the accumulated category total to exceed 500.0 (`LimiteExcedidoError`, HTTP 400).
- **FR-010**: The system MUST strictly isolate all expense operations to the authenticated user resolved from the JWT token, completely ignoring any foreign user ID provided in query parameters, path variables, or request bodies.
- **FR-011**: The system MUST support paginated expense listing via `/gastos/` with `skip` (default: 0) and `limit` (default: 20), returning HTTP 422 for negative or invalid pagination values.
- **FR-012**: The system MUST expose MCP tools `registrar_gasto` and `listar_gastos` that execute the identical business rules from `services/` and return structured dictionaries or structured error objects `{"error": "..."}`.
- **FR-013**: The system MUST adhere to the fixed compatibility contracts and function signatures from Sessions 6-8:
  - `app/services/gastos.py`: `CategoriaInvalidaError`, `LimiteExcedidoError`, `LIMITE_POR_CATEGORIA = 500.0`, `registrar_gasto(db, usuario_id, descripcion, monto, categoria, repo=gastos_repository) -> dict`, `listar_gastos(db, usuario_id, skip=0, limit=20, repo=gastos_repository) -> list[dict]`.
  - `app/repositories/gastos.py` (module with standalone functions): `guardar(db, usuario_id, descripcion, monto, categoria) -> dict`, `listar(db, usuario_id, skip=0, limit=20) -> list[dict]`, `total_por_categoria(db, usuario_id, categoria) -> float`.
  - `app/repositories/usuarios.py`: `obtener_por_email(db, email) -> Usuario | None`, `guardar(db, email, hashed_password) -> Usuario`.
  - `app.database.get_db`, `app.dependencies.get_current_user`, `app.dependencies.get_gastos_repo`, `app.models.usuario.Usuario(id=, email=, hashed_password=)`.
  - `tests/__init__.py` present; `test_api_gastos.py` importing `from tests.test_gastos import RepositorioFalso`.

### Key Entities *(include if feature involves data)*

- **Usuario**: Represents an individual registered user of the system.
  - Attributes: `id` (integer primary key), `email` (string, unique, non-empty), `hashed_password` (string, bcrypt hash, confidential).
  - Relationships: 1-to-many relationship with Gasto.
- **Gasto**: Represents an individual expense transaction recorded by a user.
  - Attributes: `id` (integer primary key), `usuario_id` (foreign key referencing Usuario), `descripcion` (string, non-empty), `monto` (float, strictly > 0), `categoria` (string, one of four allowed categories), `fecha` (timestamp/datetime).
  - Relationships: Belongs to exactly one Usuario.
- **Categoria**: Predefined domain enumeration representing allowable expense categories: `comida`, `transporte`, `entretenimiento`, `otros`, with an enforced maximum cumulative spending cap of 500.0 per user.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of invalid expense creation attempts (amount <= 0, empty description, unrecognized category, or exceeding the 500.0 limit) are rejected with precise business errors and appropriate HTTP status codes.
- **SC-002**: Zero cross-user data leakage: In 100% of test verification scenarios, a user can only access and modify their own expense data, even when explicitly specifying another user's ID in request parameters.
- **SC-003**: 100% functional parity between REST endpoints and MCP tools regarding business rules, validation, and user identity scoping.
- **SC-004**: Users complete expense registration and listing operations in under 200 milliseconds under standard operating conditions.
- **SC-005**: 100% of specified business rules are covered by automated tests, satisfying constitution thresholds: `>= 90%` coverage in `services/` and `>= 80%` global coverage across `services + repositories + routers + utils`.
- **SC-006**: 100% passing tests across all test suites (unit, integration, and API) including mandatory compatibility tests from Sessions 6-8.

## Assumptions

- Monetary values are handled in a single standard currency representation across all calculations.
- The 500.0 category limit applies to the cumulative total of all active expenses for that user and category.
- Expense categories are case-sensitive and must be provided in lowercase: `comida`, `transporte`, `entretenimiento`, `otros`.
- In MCP environments using `stdio` transport where token propagation is unavailable, a demo user identity configured in `.env` serves as an explicitly documented fallback.
- SQLite is used as the relational database engine for development and local testing, while remaining compatible with PostgreSQL for production.
