# REST API Contract: Sistema de Control de Gastos Personales

## Convención General
- Todos los payloads de entrada y salida son JSON (`application/json`), excepto `/usuarios/token` que recibe `application/x-www-form-urlencoded` por convención OAuth2 Password Flow.
- Errores no controlados retornan `500` con `{"detail": "Error interno del servidor"}` (Artículo IV.5).
- Errores de validación de esquema Pydantic retornan `422 Unprocessable Entity`.
- Errores de reglas de negocio conocidas retornan `400 Bad Request` con `{"detail": "..."}`.
- Autenticación ausente o inválida retorna `401 Unauthorized`.

---

## 1. Registro de Usuario
- **Ruta**: `POST /usuarios/`
- **Autenticación**: Ninguna (pública)
- **Request Body**:
  ```json
  {
    "email": "usuario@ejemplo.com",
    "password": "Password123!"
  }
  ```
- **Respuestas**:
  - `201 Created`:
    ```json
    {
      "id": 1,
      "email": "usuario@ejemplo.com"
    }
    ```
  - `400 Bad Request`:
    ```json
    {
      "detail": "El email ya se encuentra registrado"
    }
    ```
  - `422 Unprocessable Entity`: Formato de email inválido o cuerpo incompleto.

---

## 2. Autenticación y Emisión de Token
- **Ruta**: `POST /usuarios/token`
- **Autenticación**: Ninguna (pública)
- **Request Format**: Form data (`application/x-www-form-urlencoded`)
  - `username`: "usuario@ejemplo.com" (email del usuario)
  - `password`: "Password123!"
- **Respuestas**:
  - `200 OK`:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    }
    ```
  - `401 Unauthorized`:
    ```json
    {
      "detail": "Credenciales inválidas"
    }
    ```

---

## 3. Registrar Gasto
- **Ruta**: `POST /gastos/`
- **Autenticación**: Requerida (`Authorization: Bearer <token>`)
- **Request Body**:
  ```json
  {
    "descripcion": "Cena de negocios",
    "monto": 85.50,
    "categoria": "comida"
  }
  ```
- **Respuestas**:
  - `201 Created`:
    ```json
    {
      "id": 10,
      "usuario_id": 1,
      "descripcion": "Cena de negocios",
      "monto": 85.50,
      "categoria": "comida",
      "fecha": "2026-09-19T16:00:00"
    }
    ```
  - `400 Bad Request` (Categoría inválida):
    ```json
    {
      "detail": "Categoría 'viajes' inválida. Permitidas: comida, transporte, entretenimiento, otros"
    }
    ```
  - `400 Bad Request` (Límite excedido):
    ```json
    {
      "detail": "El gasto excede el límite máximo acumulado de 500.0 para la categoría 'comida'"
    }
    ```
  - `401 Unauthorized`: Token faltante, expirado o manipulado.
  - `422 Unprocessable Entity`: `monto <= 0`, descripción vacía, etc.

---

## 4. Listar Gastos Paginados
- **Ruta**: `GET /gastos/`
- **Autenticación**: Requerida (`Authorization: Bearer <token>`)
- **Query Parameters**:
  - `skip` (`int`, opcional, default: `0`, ge=0)
  - `limit` (`int`, opcional, default: `20`, ge=1, le=100)
- **Respuestas**:
  - `200 OK`:
    ```json
    [
      {
        "id": 10,
        "usuario_id": 1,
        "descripcion": "Cena de negocios",
        "monto": 85.50,
        "categoria": "comida",
        "fecha": "2026-09-19T16:00:00"
      }
    ]
    ```
  - `401 Unauthorized`: Token faltante o inválido.
  - `422 Unprocessable Entity`: Parámetros `skip` o `limit` negativos o fuera de rango.

*Nota de seguridad*: `GET /gastos/` nunca expone gastos de otros usuarios ni acepta `usuario_id` en query params. Si un usuario intenta enviar `?usuario_id=99`, el backend ignora dicho parámetro y filtra exclusivamente por el `usuario_id` del token JWT verificado (Artículo IV.4 y V.1).
