# Research & Technical Decisions: Sistema de Control de Gastos Personales

## Decision 1: Arquitectura de Montaje MCP vía streamable-http en FastAPI

- **Decision**: Montar el servidor MCP dentro de la misma instancia de la aplicación FastAPI utilizando el transporte streamable-http provisto por el SDK oficial de MCP (`mcp`). La autenticación se resolverá extrayendo el token Bearer JWT desde los headers HTTP de la solicitud de sesión MCP, utilizando la misma lógica de decodificación y validación que `get_current_user`.
- **Rationale**: 
  - Cumple directamente con el Artículo VI de la Constitución: no duplica lógica de negocio ni modelos de seguridad.
  - Permite que las herramientas MCP (`registrar_gasto` y `listar_gastos`) invoquen directamente las funciones de `app/services/gastos.py`, compartiendo la misma sesión de base de datos o repositorio y el mismo contexto de usuario autenticado.
  - Soporta el modo `stdio` con usuario demo documentado en `.env` para pruebas locales de CLI sin transporte de red.
- **Alternatives considered**:
  - *Servidor MCP independiente como proceso separado*: Descartado por complejidad operativa innecesaria, duplicación de configuración y dificultad para compartir sesiones y dependencias en desarrollo.
  - *Transporte SSE legacy*: Descartado en favor de streamable-http, recomendado por el SDK oficial contemporáneo de MCP.

## Decision 2: Gestión Criptográfica de Contraseñas y Compatibilidad `passlib[bcrypt]`

- **Decision**: Utilizar `passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")` con el paquete `bcrypt` restringido a `<4.1` (ej. `bcrypt>=4.0.1,<4.1.0`).
- **Rationale**:
  - `passlib` versión 1.7.4 presenta una incompatibilidad documentada con `bcrypt >= 4.1.0` debido a la remoción interna del atributo `__about__`. Fijar `bcrypt<4.1` garantiza compatibilidad total, estabilidad y previene advertencias o errores en tiempo de ejecución.
  - Cumple estrictamente con el Artículo IV.1 de la Constitución: nunca se almacenan ni loguean contraseñas en texto plano.
- **Alternatives considered**:
  - *Uso directo de `bcrypt` sin passlib*: Descartado porque el contrato y stack requeridos estipulan `passlib[bcrypt]` para el manejo idiomático de contextos en FastAPI.
  - *`argon2` o `pbkdf2`*: Descartados porque la constitución y especificación fijan explícitamente `bcrypt`.

## Decision 3: Autenticación y Emisión de Tokens JWT con PyJWT

- **Decision**: Emplear exclusivamente `pyjwt` (no `python-jose`) para la firma y decodificación de tokens JWT usando el algoritmo `HS256`.
- **Rationale**:
  - `pyjwt` es una biblioteca moderna, activamente mantenida y sin vulnerabilidades heredadas ni dependencias criptográficas obsoletas (a diferencia de `python-jose`).
  - La configuración de expiración (`ACCESS_TOKEN_EXPIRE_MINUTES`) y clave secreta (`SECRET_KEY`) se cargan de forma segura a través de `pydantic-settings`.
- **Alternatives considered**:
  - *`python-jose`*: Descartado explícitamente en los lineamientos técnicos por falta de mantenimiento y problemas de dependencias.

## Decision 4: Inversión de Dependencias (DIP) Simple y Modular

- **Decision**: Implementar la Inversión de Dependencias (DIP) en `app/services/gastos.py` recibiendo el repositorio como argumento keyword con valor por defecto:
  ```python
  from app.repositories import gastos as gastos_repository

  def registrar_gasto(db, usuario_id, descripcion, monto, categoria, repo=gastos_repository) -> dict: ...
  def listar_gastos(db, usuario_id, skip=0, limit=20, repo=gastos_repository) -> list[dict]: ...
  ```
- **Rationale**:
  - Cumple fielmente con el Artículo II.3 de la Constitución: innegociable para posibilitar testing unitario sin `unittest.mock`.
  - Evita contenedores IoC complejos (como `dependency-injector` o pinject), manteniendo el código idiomático, directo y ligero en Python.
  - Los tests unitarios simplemente inyectan una instancia de `RepositorioFalso` en `repo`.
- **Alternatives considered**:
  - *Inyección de dependencias mediante clases abstractas / interfaces ABC*: Descartado porque los repositorios son módulos funcionales y añadir jerarquías de clases violaría la simplicidad de la constitución y el contrato inmutable de las Sesiones 6-8.
  - *Monkeypatching o `unittest.mock`*: Prohibido explícitamente por el Artículo VII.2.

## Decision 5: Agnosticismo de Persistencia y SQLite en Memoria

- **Decision**: Diseñar `app/database.py` utilizando SQLAlchemy 2.0 con detección condicional de `connect_args={"check_same_thread": False}` únicamente si la URL corresponde a SQLite. Para tests de integración, se empleará un motor SQLite en memoria (`sqlite:///:memory:`) con tablas creadas en fixture de sesión/función.
- **Rationale**:
  - Cumple con el Artículo III.2 (portabilidad transparente SQLite/PostgreSQL) y el Artículo VII.4 (tests de integración contra SQLite real en memoria).
  - Asegura que ningún service ni router contenga código específico del motor de base de datos.
- **Alternatives considered**:
  - *Mocks de base de datos en integración*: Descartado por el Artículo VII.4 que exige SQLite real en memoria.

## Decision 6: Pirámide de Testing y Cumplimiento de Cobertura

- **Decision**: Estructurar la suite de pruebas en tres niveles claramente diferenciados:
  1. `tests/unit/`: Tests unitarios de servicios (`services/`) inyectando `RepositorioFalso`. Cobertura objetivo $\ge 90\%$.
  2. `tests/integration/`: Tests de repositorios y base de datos contra SQLite en memoria.
  3. `tests/api/`: Tests de endpoints REST y MCP tools utilizando `TestClient` con `app.dependency_overrides`.
  - Ejecución de cobertura: `pytest --cov=app --cov-report=term-missing --cov-fail-under=80` omitiendo `app/main.py`, `app/mcp/*` y `app/logging_config.py`.
- **Rationale**:
  - Cumple estrictamente con el Artículo VII (Testing y Cobertura) de la Constitución.
  - Asegura que los contratos inmutables de las Sesiones 6-8 (`from tests.test_gastos import RepositorioFalso`) se respeten al 100%.
- **Alternatives considered**:
  - *Solo tests de API / integración*: Descartado porque no garantiza la rapidez de feedback ni el aislamiento exigido por la pirámide de pruebas.
