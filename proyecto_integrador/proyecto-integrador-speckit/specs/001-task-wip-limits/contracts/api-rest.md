# Contrato de API REST: Sistema de Gestión de Tareas

**Feature**: `001-task-wip-limits` | **Versión**: 1.0.0

Este documento especifica formalmente los contratos HTTP, cabeceras, códigos semánticos y esquemas de payload para todos los endpoints expuestos por la aplicación FastAPI.

---

## Convención de Códigos y Errores HTTP

Conforme al **Artículo V.1**:
- `201 Created`: Recurso creado exitosamente.
- `200 OK`: Consulta, listado o actualización de estado exitosa.
- `204 No Content`: Eliminación exitosa sin cuerpo de respuesta.
- `400 Bad Request`: Error de regla de negocio conocido (`{"detail": "<ErrorClass>: <Mensaje>"}`).
- `401 Unauthorized`: Token ausente, expirado o credenciales inválidas (`{"detail": "No autenticado"}`).
- `403 Forbidden`: Tarea existente pero perteneciente a otro usuario (`{"detail": "No tiene permiso para acceder a este recurso"}`).
- `404 Not Found`: Recurso inexistente en el sistema (`{"detail": "Recurso no encontrado"}`).
- `422 Unprocessable Entity`: Error de validación de esquema Pydantic (tipos, campos requeridos).
- `500 Internal Server Error`: Excepción no controlada (`{"detail": "Error interno del servidor"}`).

---

## 1. Endpoints de Usuario y Autenticación

### 1.1 Registrar Usuario
- **Ruta**: `POST /usuarios/`
- **Autenticación**: Pública
- **Request Body** (`application/json`):
  ```json
  {
    "email": "usuario@ejemplo.com",
    "password": "miPasswordSeguro123"
  }
  ```
- **Respuestas**:
  - **201 Created**:
    ```json
    {
      "id": 1,
      "email": "usuario@ejemplo.com",
      "creado_en": "2026-09-21T20:00:00Z"
    }
    ```
  - **400 Bad Request** (Email duplicado):
    ```json
    { "detail": "El correo electrónico ya se encuentra registrado" }
    ```
  - **422 Unprocessable Entity**: Formato de email incorrecto o contraseña menor a 8 caracteres.

---

### 1.2 Iniciar Sesión y Obtener Token JWT
- **Ruta**: `POST /usuarios/token`
- **Autenticación**: Pública
- **Content-Type**: `application/x-www-form-urlencoded`
- **Request Body**:
  - `username`: `usuario@ejemplo.com`
  - `password`: `miPasswordSeguro123`
- **Respuestas**:
  - **200 OK**:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
      "token_type": "bearer"
    }
    ```
  - **401 Unauthorized**:
    ```json
    { "detail": "Credenciales inválidas" }
    ```

---

## 2. Endpoints de Tareas

Todos los endpoints bajo `/tareas/` requieren la cabecera:
`Authorization: Bearer <access_token>`

### 2.1 Crear Tarea
- **Ruta**: `POST /tareas/`
- **Request Body** (`application/json`):
  ```json
  {
    "titulo": "Preparar demo para cliente",
    "descripcion": "Revisar flujos y pantallas de configuración",
    "prioridad": "alta",
    "fecha_limite": "2026-09-30T18:00:00Z"
  }
  ```
- **Respuestas**:
  - **201 Created**:
    ```json
    {
      "id": 10,
      "usuario_id": 1,
      "titulo": "Preparar demo para cliente",
      "descripcion": "Revisar flujos y pantallas de configuración",
      "prioridad": "alta",
      "estado": "pendiente",
      "fecha_limite": "2026-09-30T18:00:00Z",
      "creado_en": "2026-09-21T21:00:00Z",
      "actualizado_en": "2026-09-21T21:00:00Z"
    }
    ```
  - **400 Bad Request** (Límite de prioridad alta excedido):
    ```json
    { "detail": "LimitePrioridadAltaExcedidoError: No se pueden tener más de 2 tareas de prioridad alta abiertas simultáneamente" }
    ```
  - **422 Unprocessable Entity**: Título vacío o prioridad fuera del Enum (`baja`, `media`, `alta`).

---

### 2.2 Listar Tareas Personales
- **Ruta**: `GET /tareas/`
- **Parámetros Query**:
  - `skip` (int, opcional, default: `0`): Desplazamiento para paginación.
  - `limit` (int, opcional, default: `20`): Cantidad máxima de registros.
  - `estado` (string, opcional): Filtrar por `pendiente`, `en_progreso`, `completada`.
  - `prioridad` (string, opcional): Filtrar por `baja`, `media`, `alta`.
- **Ordenamiento**: Descendente por fecha de creación e ID (`creado_en` desc, `id` desc).
- **Respuestas**:
  - **200 OK**:
    ```json
    [
      {
        "id": 10,
        "usuario_id": 1,
        "titulo": "Preparar demo para cliente",
        "descripcion": "Revisar flujos y pantallas de configuración",
        "prioridad": "alta",
        "estado": "pendiente",
        "fecha_limite": "2026-09-30T18:00:00Z",
        "creado_en": "2026-09-21T21:00:00Z",
        "actualizado_en": "2026-09-21T21:00:00Z"
      }
    ]
    ```

---

### 2.3 Consultar Detalle de Tarea
- **Ruta**: `GET /tareas/{id}`
- **Respuestas**:
  - **200 OK**: Retorna el objeto `TareaOut`.
  - **403 Forbidden**: Si la tarea pertenece a otro usuario.
  - **404 Not Found**: Si la tarea no existe en el sistema.

---

### 2.4 Actualizar Estado de Tarea
- **Ruta**: `PATCH /tareas/{id}/estado`
- **Request Body** (`application/json`):
  ```json
  {
    "estado": "en_progreso"
  }
  ```
- **Respuestas**:
  - **200 OK**: Retorna el objeto `TareaOut` actualizado.
  - **400 Bad Request** (Límite WIP excedido):
    ```json
    { "detail": "LimiteWIPExcedidoError: No se pueden tener más de 3 tareas en progreso simultáneamente" }
    ```
  - **400 Bad Request** (Transición inválida):
    ```json
    { "detail": "TransicionEstadoInvalidaError: No se permite pasar directamente de 'pendiente' a 'completada'" }
    ```
  - **403 Forbidden**: Si la tarea pertenece a otro usuario.
  - **404 Not Found**: Si la tarea no existe.

---

### 2.5 Eliminar Tarea
- **Ruta**: `DELETE /tareas/{id}`
- **Respuestas**:
  - **204 No Content**: Tarea eliminada exitosamente (cuerpo vacío).
  - **403 Forbidden**: Si la tarea pertenece a otro usuario.
  - **404 Not Found**: Si la tarea no existe.
