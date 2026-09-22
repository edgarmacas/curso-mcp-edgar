# Technical Research & Architecture Decisions: Sistema de Gestión de Tareas con Límite de Capacidad

**Feature**: `001-task-wip-limits` | **Date**: 2026-09-21

Este documento consolida las decisiones técnicas, fundamentos de arquitectura y mejores prácticas adoptadas para satisfacer la especificación técnica y las directrices constitucionales del proyecto.

---

## 1. Integración de MCP (Model Context Protocol) en FastAPI

### Decisión
Utilizar el SDK oficial de Python `mcp` para exponer las herramientas (`crear_tarea`, `listar_tareas`, `iniciar_tarea_prioritaria`), montándolas en la aplicación FastAPI mediante transporte HTTP streamable / SSE y proporcionando un punto de entrada CLI para transporte `stdio`.

### Justificación
- **Reutilización de servicios (Artículo VI.1)**: Tanto los endpoints REST como las herramientas MCP llaman a las mismas funciones en `app/services/tareas_service.py`, evitando duplicidad de reglas de negocio.
- **Manejo de errores estructurados (Artículo VI.3)**: Las excepciones de negocio capturadas en las tools retornan diccionarios JSON `{"error": "NombreError: Mensaje"}`, preservando la estabilidad de la sesión del agente LLM.
- **Resolución de identidad en stdio**: En transporte stdio (usado por clientes locales como Claude Desktop o Cursor), la identidad del usuario se resuelve a partir de la variable de entorno `MCP_USER_EMAIL` con fallback a un usuario de prueba documentado, resolviendo la falta de cabeceras HTTP en dicho transporte.

### Alternativas Consideradas
- *Servidor MCP como proceso independiente con duplicación de código*: Descartada porque violaría el Artículo VI.1 y complicaría el despliegue y mantenimiento.
- *Implementación manual de JSON-RPC*: Descartada por innecesaria; el SDK oficial de MCP provee validación de esquemas JSON y gestión de ciclo de vida estándar.

---

## 2. Inyección de Dependencias (DIP) y Prohibición de Mocks en Servicios

### Decisión
Implementar el Principio de Inversión de Dependencias (DIP) en `app/services/tareas_service.py` mediante parámetros de función con valor por defecto:
```python
def crear_tarea(datos: TareaCreate, usuario_id: int, repo=default_tareas_repo) -> Tarea:
    ...
```
Para las pruebas unitarias, se inyectará una implementación falsa en memoria (`FakeTareasRepository`) que emula las operaciones de persistencia mediante diccionarios en memoria.

### Justificación
- **Cumplimiento estricto del Artículo II.3 y VII.2**: El Artículo II.3 establece que todo service recibe su repositorio como parámetro con valor por defecto y prohíbe importarlo fijo en el cuerpo. El Artículo VII.2 prohíbe explícitamente el uso de `unittest.mock` en los tests unitarios de services.
- **Pruebas deterministas y ultrarrápidas**: La suite de pruebas unitarias ejecuta en milisegundos sin iniciar conexiones a base de datos ni lidiar con la fragilidad de parches dinámicos (`patch`).

### Alternativas Consideradas
- *Uso de clases de servicio con constructores pesados*: Descartada por sobre-ingeniería innecesaria; funciones con parámetros por defecto son idiomáticas en Python y cumplen al 100% con DIP.
- *Uso de `unittest.mock.MagicMock`*: Prohibido explícitamente por la Constitución.

---

## 3. Seguridad de Credenciales y Fijación de Versiones

### Decisión
Utilizar `passlib[bcrypt]` fijando explícitamente `bcrypt<4.1` en el gestor de dependencias. Para la emisión y validación de tokens de acceso, utilizar `pyjwt` con algoritmo simétrico `HS256` y expiración finita configurable vía `pydantic-settings`.

### Justificación
- **Compatibilidad técnica comprobada**: `passlib` 1.7.4 presenta una incompatibilidad documentada con versiones de `bcrypt >= 4.1.0` debido a cambios en la API interna de `__about__`. Fijar `bcrypt<4.1` garantiza funcionamiento estable y seguro.
- **Prevención de fugas de contraseñas (Artículo IV.1)**: La contraseña en texto plano se descarta inmediatamente después del hash; los modelos y DTOs de salida (`UsuarioOut`) omiten de forma estricta el campo `password_hash`.
- **Autorización estricta (Artículo IV.4)**: La dependencia FastAPI `get_current_user` decodifica el token JWT y obtiene la entidad del usuario. Todo acceso a recursos utiliza el `usuario_id` verificado, previniendo vulnerabilidades de Insecure Direct Object Reference (IDOR).

### Alternativas Consideradas
- *Librería `argon2-cffi`*: Descartada debido a que el Artículo IV.1 de la constitución exige expresamente bcrypt.
- *Tokens sin expiración o expiración infinita*: Prohibidos por el Artículo IV.2.

---

## 4. Persistencia Agnóstica y Aislamiento Multi-inquilino

### Decisión
Utilizar SQLAlchemy 2.0 con `DeclarativeBase`. La configuración de la conexión en `app/database.py` detecta el tipo de base de datos a partir de `DATABASE_URL` y aplica `connect_args={"check_same_thread": False}` únicamente si el dialecto es SQLite.

```python
engine_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}
engine = create_engine(settings.DATABASE_URL, **engine_args)
```

En la capa de persistencia (`app/repositories/tareas_repository.py`), cada consulta de lectura, conteo, actualización o eliminación exige el parámetro `usuario_id` y aplica `.filter(Tarea.usuario_id == usuario_id)`.

### Justificación
- **Cumplimiento del Artículo III.1 y III.2**: Permite trabajar con SQLite en desarrollo y pruebas locales y migrar a PostgreSQL en producción modificando únicamente la variable de entorno `.env`, sin tocar una sola línea de código en routers o services.
- **Aislamiento absoluto**: Impide que un usuario acceda accidentalmente a tareas ajenas, incluso en operaciones masivas o de conteo.

### Alternativas Consideradas
- *Filtros de base de datos globales (Row-Level Security nativo en BD)*: Agrega complejidad excesiva para desarrollo local con SQLite; el filtro explícito en repositorio es transparente y verificable.

---

## 5. Estrategia de la Pirámide de Testing

### Decisión
Estructurar los tests en tres niveles complementarios en `tests/`:

1. **Pruebas Unitarias (`tests/unit/test_services_tareas.py`)**:
   - Inyectan `FakeTareasRepository`.
   - Verifican el 100% de las reglas de negocio:
     - Límite de 2 tareas de prioridad alta abiertas (`LimitePrioridadAltaExcedidoError`).
     - Límite de 3 tareas en estado `en_progreso` (`LimiteWIPExcedidoError`).
     - Secuencia de transición permitida (`TransicionEstadoInvalidaError`).
   - Sin dependencias de base de datos ni mocks.
2. **Pruebas de Integración (`tests/integration/test_repositories.py`)**:
   - Ejecutan contra SQLite en memoria creando tablas con `Base.metadata.create_all`.
   - Prueban aislamiento por usuario, persistencia, conteo y ordenamiento.
3. **Pruebas de API y MCP (`tests/api/`)**:
   - Utilizan `httpx.AsyncClient` y `TestClient` contra la aplicación FastAPI.
   - Aplican `app.dependency_overrides[get_db]` para usar la base de datos de test en memoria.
   - Validan códigos HTTP (201, 200, 204, 400, 401, 403, 404, 422) y el protocolo MCP.

### Cobertura Objetivo
- $\ge 90\%$ en `app/services/`
- $\ge 70\%$ global combinada (`app/services`, `app/repositories`, `app/routers`, `app/utils`)
- Reporte medido con: `pytest --cov=app --cov-report=term-missing` omitiendo `main.py`, `mcp/*` y `logging_config.py`.
