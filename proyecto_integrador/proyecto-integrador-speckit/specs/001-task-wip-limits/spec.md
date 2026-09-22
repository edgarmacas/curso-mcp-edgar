# Feature Specification: Sistema de Gestión de Tareas Personales con Límite de Capacidad (WIP Limits)

**Feature Branch**: `001-task-wip-limits`

**Created**: 2026-09-21

**Status**: Draft

**Input**: User description: "Sistema de gestión de tareas personales con límite de capacidad (WIP limits)."

## Clarifications

### Session 2026-09-21
- Q: ¿Cómo debe resolverse la identidad del usuario en el transporte stdio de MCP cuando no se dispone de cabeceras HTTP con token JWT? → A: Mediante la variable de entorno `MCP_USER_EMAIL` leída al inicio del servidor stdio, con fallback documentado a un usuario de prueba predeterminado si no está definida.
- Q: ¿Cuál debe ser el ordenamiento por defecto de las tareas al consultarlas en GET /tareas/ y listar_tareas? → A: Orden descendente por fecha de creación / ID (las tareas más recientes aparecen primero).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registro y Autenticación de Usuario (Priority: P1)

Como usuario del sistema, quiero registrar una cuenta personal con mi email y contraseña, y obtener un token de autenticación seguro para acceder a mi espacio privado de tareas sin que nadie más pueda verlas.

**Why this priority**: Es la base de seguridad y aislamiento multi-inquilino del sistema. Sin identidad de usuario autenticada, no se puede garantizar la propiedad ni el aislamiento de las tareas ni los límites individuales.

**Independent Test**: Registrar un usuario con credenciales válidas y realizar login para obtener el token JWT; verificar que no expone la contraseña en las respuestas y que credenciales inválidas o duplicadas son rechazadas adecuadamente.

**Acceptance Scenarios**:

1. **Given** un email no registrado y una contraseña válida, **When** el usuario solicita el registro vía POST `/usuarios/`, **Then** el sistema responde HTTP 201 con los datos del usuario creado (excluyendo la contraseña).
2. **Given** un email ya registrado, **When** se intenta registrar una nueva cuenta con ese mismo email, **Then** el sistema responde HTTP 400 indicando email duplicado.
3. **Given** credenciales de usuario correctas, **When** el usuario solicita un token vía POST `/usuarios/token`, **Then** el sistema responde HTTP 200 con un token JWT firmado y con tiempo de expiración finito.
4. **Given** credenciales de usuario incorrectas, **When** se solicita autenticación, **Then** el sistema responde HTTP 401 Unauthorized.

---

### User Story 2 - Creación de Tareas y Control de Límite de Prioridad Alta (Priority: P1)

Como usuario autenticado, quiero crear tareas personales definiendo título, descripción opcional, fecha límite opcional y prioridad (`baja`, `media`, `alta`), asegurando que no pueda saturarme con más de 2 tareas de prioridad alta abiertas simultáneamente.

**Why this priority**: Evita la sobrecarga cognitiva y asegura el foco en prioridades críticas, haciendo cumplir la regla de negocio central de capacidad por prioridad.

**Independent Test**: Crear tareas con diferentes prioridades y comprobar que al intentar registrar una tercera tarea de prioridad alta en estado abierto ("pendiente" o "en_progreso") el sistema rechaza la operación con `LimitePrioridadAltaExcedidoError`.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado con menos de 2 tareas de prioridad alta abiertas, **When** crea una tarea con título no vacío y prioridad `alta`, **Then** el sistema crea la tarea en estado `pendiente` con HTTP 201 y asignada a su identificador de usuario.
2. **Given** un usuario con 2 tareas de prioridad `alta` abiertas (en estado `pendiente` o `en_progreso`), **When** intenta crear una tercera tarea de prioridad `alta`, **Then** la solicitud es rechazada con HTTP 400 y mensaje `LimitePrioridadAltaExcedidoError`.
3. **Given** un intento de creación de tarea con título vacío o valor de prioridad fuera de (`baja`, `media`, `alta`), **When** se envía la solicitud, **Then** el sistema responde con error de validación HTTP 422.
4. **Given** un usuario con 2 tareas de prioridad `alta` completadas, **When** crea una nueva tarea de prioridad `alta`, **Then** la tarea se crea exitosamente porque las tareas completadas no cuentan como abiertas.

---

### User Story 3 - Gestión de Flujo de Trabajo y Límite WIP (Work In Progress) (Priority: P1)

Como usuario autenticado, quiero avanzar el estado de mis tareas a través de las fases de trabajo ("pendiente" -> "en_progreso" -> "completada"), con la garantía de que no puedo tener más de 3 tareas en progreso al mismo tiempo ni saltar fases de trabajo sin haberlas iniciado.

**Why this priority**: Implementa la disciplina Kanban central de límite WIP (máximo 3 tareas en progreso) y la integridad de transiciones de ciclo de vida del producto.

**Independent Test**: Mover tareas de `pendiente` a `en_progreso` hasta alcanzar el límite de 3; intentar mover una cuarta tarea y verificar el error `LimiteWIPExcedidoError`; intentar pasar una tarea de `pendiente` directamente a `completada` y verificar `TransicionEstadoInvalidaError`.

**Acceptance Scenarios**:

1. **Given** una tarea propia en estado `pendiente` y menos de 3 tareas en estado `en_progreso`, **When** el usuario actualiza el estado a `en_progreso`, **Then** el sistema responde HTTP 200 con la tarea actualizada.
2. **Given** un usuario con 3 tareas en estado `en_progreso`, **When** intenta cambiar el estado de otra tarea a `en_progreso`, **Then** el sistema rechaza la operación con HTTP 400 y mensaje `LimiteWIPExcedidoError`.
3. **Given** una tarea en estado `pendiente`, **When** el usuario intenta cambiar su estado directamente a `completada`, **Then** el sistema rechaza la operación con HTTP 400 y mensaje `TransicionEstadoInvalidaError`.
4. **Given** una tarea en estado `en_progreso`, **When** el usuario actualiza su estado a `completada`, **Then** el sistema actualiza la tarea a `completada` con HTTP 200, liberando un cupo de WIP.

---

### User Story 4 - Consulta, Filtrado y Aislamiento de Tareas (Priority: P2)

Como usuario autenticado, quiero listar mis tareas con soporte de paginación y filtros por estado y prioridad, así como consultar una tarea puntual por su ID, asegurándome de que jamás podré visualizar tareas de otros usuarios.

**Why this priority**: Permite la visibilidad y seguimiento de las tareas manteniendo la confidencialidad absoluta de los datos entre usuarios.

**Independent Test**: Crear tareas para el usuario A y el usuario B; autenticar a A y verificar que al listar tareas solo aparecen las suyas; verificar que si A intenta consultar por ID una tarea de B recibe HTTP 403 Forbidden.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado con tareas registradas, **When** solicita el listado GET `/tareas/` con parámetros `skip` y `limit`, **Then** recibe una lista paginada ordenada descendentemente por fecha de creación/ID (más recientes primero) que contiene únicamente sus tareas.
2. **Given** parámetros opcionales de consulta `estado` o `prioridad`, **When** el usuario realiza la consulta, **Then** el listado retorna solo las tareas que cumplen los criterios de filtro indicados.
3. **Given** una tarea existente que pertenece a otro usuario, **When** el usuario autenticado intenta consultarla mediante GET `/tareas/{id}`, **Then** el sistema responde HTTP 403 Forbidden.
4. **Given** un ID de tarea que no existe en el sistema, **When** el usuario intenta consultarla, **Then** el sistema responde HTTP 404 Not Found.
5. **Given** una solicitud a endpoints de tareas sin cabecera de autenticación válida, **When** se envía la petición, **Then** el sistema responde HTTP 401 Unauthorized.

---

### User Story 5 - Eliminación Segura de Tareas (Priority: P3)

Como usuario autenticado, quiero poder eliminar tareas que ya no son relevantes, asegurando que solo puedo eliminar las mías y que se verifique la propiedad antes de proceder.

**Why this priority**: Mantiene limpia la lista de tareas del usuario sin comprometer la seguridad de datos ajenos.

**Independent Test**: Eliminar una tarea propia y verificar código HTTP 204 y su desaparición en posteriores consultas; intentar eliminar una tarea de otro usuario y verificar HTTP 403.

**Acceptance Scenarios**:

1. **Given** una tarea existente perteneciente al usuario autenticado, **When** envía una solicitud DELETE `/tareas/{id}`, **Then** el sistema elimina la tarea y responde HTTP 204 No Content.
2. **Given** una tarea existente perteneciente a otro usuario, **When** el usuario intenta eliminarla, **Then** el sistema responde HTTP 403 Forbidden y la tarea no se elimina.
3. **Given** una solicitud para eliminar una tarea con un ID inexistente, **When** se envía la petición, **Then** el sistema responde HTTP 404 Not Found.

---

### User Story 6 - Asistencia Automatizada mediante MCP (Model Context Protocol) (Priority: P2)

Como usuario asistido por un agente de inteligencia artificial, quiero interactuar con mis tareas a través de herramientas MCP (`crear_tarea`, `listar_tareas`, `iniciar_tarea_prioritaria`) con la certeza de que el agente opera bajo mi identidad y respeta estrictamente las mismas reglas de capacidad y validaciones que la API REST.

**Why this priority**: Expone la funcionalidad de gestión personal a agentes LLM de forma segura, reutilizando la lógica de negocio sin duplicidad de código.

**Independent Test**: Invocar las herramientas MCP en una sesión autenticada; verificar que `crear_tarea` valida el límite de prioridad alta, `iniciar_tarea_prioritaria` selecciona la tarea pendiente de mayor prioridad respetando el límite WIP de 3, y los errores de negocio se entregan en formato `{"error": "..."}` sin romper la sesión.

**Acceptance Scenarios**:

1. **Given** una sesión MCP activa de un usuario con menos de 2 tareas de prioridad alta abiertas, **When** el agente invoca `crear_tarea(titulo, prioridad, descripcion)`, **Then** la tarea se crea y se retorna su representación estructurada.
2. **Given** una sesión MCP con 2 tareas de prioridad alta abiertas, **When** el agente invoca `crear_tarea` con prioridad `alta`, **Then** la herramienta retorna `{"error": "LimitePrioridadAltaExcedidoError: ..."}` manteniendo la sesión MCP estable.
3. **Given** tareas en estado `pendiente` con distintas prioridades y menos de 3 tareas en progreso, **When** el agente invoca `iniciar_tarea_prioritaria()`, **Then** la tarea pendiente de mayor prioridad (`alta` antes que `media`, `media` antes que `baja`) cambia a `en_progreso`.
4. **Given** 3 tareas ya en progreso, **When** el agente invoca `iniciar_tarea_prioritaria()`, **Then** la herramienta retorna `{"error": "LimiteWIPExcedidoError: ..."}` sin modificar ninguna tarea.
5. **Given** una sesión MCP en transporte stdio, **When** se inicializa el servidor, **Then** la identidad del usuario activo se resuelve desde `MCP_USER_EMAIL` (o usuario de prueba documentado por defecto) y todas las operaciones afectan únicamente a ese usuario, sin aceptar un identificador arbitrario como parámetro.

---

### Edge Cases

- **Cambio de prioridad a "alta" en tarea existente**: Si una tarea existente de prioridad `media` o `baja` intenta cambiar su prioridad a `alta` cuando el usuario ya tiene 2 tareas de prioridad alta abiertas, debe rechazarse con `LimitePrioridadAltaExcedidoError`.
- **Transición de tarea ya completada**: Intentar modificar el estado de una tarea que ya está `completada` debe ser rechazado con `TransicionEstadoInvalidaError`.
- **Invocación de `iniciar_tarea_prioritaria` sin tareas pendientes**: Si no hay ninguna tarea en estado `pendiente`, la tool debe retornar un mensaje estructurado indicando que no hay tareas pendientes para iniciar.
- **Empate en prioridad en `iniciar_tarea_prioritaria`**: Si hay múltiples tareas pendientes con la misma prioridad más alta, se selecciona la más antigua (menor fecha de creación / menor ID).
- **Parámetros de paginación fuera de rango**: Valores negativos de `skip` o valores de `limit <= 0` o excesivamente grandes deben ser rechazados con HTTP 422.
- **Manipulación de IDs ajenos en URLs**: Cualquier intento de enviar IDs de tareas que pertenecen a otros usuarios en endpoints protegidos (GET, PATCH, DELETE) debe responder indefectiblemente 403 Forbidden.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Gestión de Usuarios)**: El sistema DEBE permitir el registro de usuarios requiriendo email y contraseña. El email DEBE ser único en el sistema. Las contraseñas NUNCA deben exponerse en respuestas y DEBEN ser almacenadas con hash seguro (`passlib[bcrypt]` con `bcrypt<4.1`).
- **FR-002 (Autenticación JWT)**: El sistema DEBE autenticar usuarios mediante OAuth2 Password Flow (`/usuarios/token`) y generar tokens JWT firmados con algoritmo `HS256`, con tiempo de expiración configurable.
- **FR-003 (Esquema de Tareas)**: El sistema DEBE requerir título no vacío y prioridad para toda tarea. La descripción y fecha límite DEBEN ser opcionales.
- **FR-004 (Enums de Dominio)**: Los valores válidos para prioridad DEBEN ser exactamente `baja`, `media`, `alta`. Los valores válidos para estado DEBEN ser exactamente `pendiente`, `en_progreso`, `completada`. Cualquier otro valor DEBE ser rechazado en la capa de validación.
- **FR-005 (Límite de Prioridad Alta)**: Un usuario NO PUEDE tener más de 2 tareas de prioridad `alta` abiertas simultáneamente (en estado `pendiente` o `en_progreso`). Si se intenta crear o cambiar una tarea a prioridad alta superando este límite, el sistema DEBE rechazar la solicitud con el error de negocio `LimitePrioridadAltaExcedidoError` (HTTP 400).
- **FR-006 (Límite WIP)**: Un usuario NO PUEDE tener más de 3 tareas en estado `en_progreso` al mismo tiempo. Si se intenta mover una cuarta tarea a `en_progreso`, el sistema DEBE rechazar la solicitud con el error de negocio `LimiteWIPExcedidoError` (HTTP 400).
- **FR-007 (Transición Válida de Estados)**: Las tareas solo pueden avanzar siguiendo la secuencia estricta `pendiente` -> `en_progreso` -> `completada`. No se permite pasar directamente de `pendiente` a `completada` sin pasar antes por `en_progreso`. Toda transición inválida DEBE ser rechazada con `TransicionEstadoInvalidaError` (HTTP 400).
- **FR-008 (Aislamiento y Autorización Estricta)**: Cada tarea DEBE pertenecer a un usuario mediante `usuario_id`. Un usuario solo puede listar, consultar, actualizar y eliminar sus propias tareas. El `usuario_id` DEBE extraerse siempre del token JWT verificado y NUNCA de parámetros enviados por el cliente. El acceso o modificación de tareas de otro usuario DEBE retornar HTTP 403 Forbidden.
- **FR-009 (Contrato API REST)**:
  - `POST /usuarios/`: Código 201 en éxito; 400 si email duplicado; 422 en error de validación.
  - `POST /usuarios/token`: Código 200 en éxito con JWT; 401 si credenciales inválidas.
  - `POST /tareas/`: Código 201 en éxito; 400 si límite prioridad alta excedido; 401 sin auth; 422 si datos inválidos.
  - `GET /tareas/`: Código 200 con lista paginada (`skip` por defecto 0, `limit` por defecto 20, orden descendente por fecha de creación/ID por defecto) y filtros (`estado`, `prioridad`); 401 sin auth; 422 si parámetros inválidos.
  - `GET /tareas/{id}`: Código 200 en éxito; 401 sin auth; 403 si pertenece a otro usuario; 404 si no existe.
  - `PATCH /tareas/{id}/estado`: Código 200 en éxito; 400 si límite WIP excedido o transición inválida; 401 sin auth; 403 si pertenece a otro usuario; 404 si no existe.
  - `DELETE /tareas/{id}`: Código 204 en éxito; 401 sin auth; 403 si pertenece a otro usuario; 404 si no existe.
- **FR-010 (Contrato MCP)**:
  - Tool `crear_tarea(titulo, prioridad, descripcion=None)`: Crea una tarea ejecutando la misma lógica de negocio que el servicio REST, validando el límite de tareas de prioridad alta.
  - Tool `listar_tareas(skip=0, limit=20, estado=None)`: Lista tareas del usuario autenticado ordenadas descendentemente por fecha de creación/ID por defecto, con soporte de filtros y paginación.
  - Tool `iniciar_tarea_prioritaria()`: Localiza la tarea pendiente con mayor prioridad del usuario y la avanza a `en_progreso`, validando el cupo WIP de máximo 3 tareas en progreso.
  - Todas las tools DEBEN operar sobre la identidad del usuario resuelta desde la sesión MCP (en transporte stdio, resuelta desde la variable de entorno `MCP_USER_EMAIL` con fallback a usuario de prueba predeterminado) y DEBEN devolver errores de negocio estructurados como `{"error": "..."}` sin romper la sesión del protocolo.
- **FR-011 (Arquitectura y DIP)**: La lógica de negocio DEBE residir exclusivamente en `services/`. Los services DEBEN recibir sus dependencias de repositorio por parámetro con valor por defecto (DIP), sin importar SQLAlchemy ni Session directamente, permitiendo su testeo unitario sin `unittest.mock`.
- **FR-012 (Garantía de Testing y Cobertura)**: El sistema DEBE contar con pruebas unitarias para el 100% de las reglas de negocio de este documento sin utilizar `unittest.mock` (inyectando repositorios falsos). La cobertura mínima en `services/` DEBE ser $\ge 90\%$ y la cobertura global combinada DEBE ser $\ge 70\%$.

### Key Entities

- **Usuario**:
  - `id`: Identificador único numérico/UUID.
  - `email`: Correo electrónico único y validado.
  - `password_hash`: Hash seguro de la contraseña.
  - `creado_en`: Marca de tiempo de registro.
- **Tarea**:
  - `id`: Identificador único numérico.
  - `usuario_id`: Identificador del usuario propietario (clave foránea obligatoria).
  - `titulo`: Cadena no vacía descriptiva del objetivo de la tarea.
  - `descripcion`: Texto opcional con detalles adicionales.
  - `prioridad`: Valor restringido al Enum (`baja`, `media`, `alta`).
  - `estado`: Valor restringido al Enum (`pendiente`, `en_progreso`, `completada`).
  - `fecha_limite`: Fecha/hora límite opcional para la tarea.
  - `creado_en`: Marca de tiempo de creación.
  - `actualizado_en`: Marca de tiempo de última actualización.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los intentos de violar las reglas de negocio (crear > 2 tareas de prioridad alta abiertas, mover > 3 tareas a `en_progreso`, o saltar de `pendiente` a `completada`) son rechazados de manera determinista con los códigos y mensajes de error especificados.
- **SC-002**: Se garantiza el 100% de aislamiento de datos: ninguna consulta o modificación permite a un usuario visualizar o alterar tareas pertenecientes a otro usuario (0 incidentes de IDOR).
- **SC-003**: El 100% de las herramientas MCP reutilizan la capa de servicios subyacente y devuelven respuestas de error estructuradas con formato `{"error": "..."}` en caso de excepción de negocio.
- **SC-004**: La suite de pruebas automatizadas ejecuta y aprueba en verde el 100% de los casos de prueba de reglas de negocio identificados, logrando una cobertura de líneas $\ge 90\%$ en `services/` y $\ge 70\%$ en cobertura global combinada.
- **SC-005**: Las operaciones comunes de la API (crear, listar, cambiar estado) responden en menos de 200 ms en entorno de pruebas local.

## Assumptions

- **Persistencia**: Para el entorno de desarrollo y pruebas locales se utiliza SQLite con diseño de repositorio agnóstico compatible con PostgreSQL para entornos de despliegue.
- **Formato de Errores de Negocio**: Los errores controlados de negocio en endpoints REST devuelven el esquema estándar FastAPI `{"detail": "<Mensaje o Clase del Error>"}`.
- **Manejo de Errores Críticos**: Excepciones no controladas devuelven HTTP 500 con el mensaje `{"detail": "Error interno del servidor"}`, protegiendo la información sensible de stack traces.
- **Transporte MCP**: El servidor MCP opera inicialmente sobre transporte stdio o SSE con autenticación resuelta desde el contexto de la sesión.
