# MCP Tools Contract: Sistema de Control de Gastos Personales

## Protocolo y Transporte
- **Transporte Primario**: `streamable-http` montado sobre la aplicación FastAPI.
- **Resolución de Identidad**: El token JWT es provisto en el header `Authorization: Bearer <token>` de la conexión HTTP MCP y validado por la lógica de seguridad compartida con la API.
- **Transporte de Respaldo (`stdio`)**: En modo local sin transporte de red ni propagación de identidad, se documenta el uso de un usuario demo (`DEMO_USER_EMAIL`) preconfigurado en `.env` (Artículo VI.4).
- **Manejo de Errores**: Todo error de negocio se retorna estructurado como `{"error": "mensaje descriptivo"}`, evitando el colapso del proceso o excepciones no controladas en el servidor MCP (Artículo VI.3).

---

## 1. Tool `registrar_gasto`

### Descripción
Registra un nuevo gasto financiero para el usuario autenticado. Aplica las mismas validaciones de negocio que la API REST: monto estrictamente positivo, categoría permitida (`comida`, `transporte`, `entretenimiento`, `otros`) y límite acumulado de `500.0` por categoría.

### Parámetros de Entrada (JSON Schema)
```json
{
  "type": "object",
  "properties": {
    "descripcion": {
      "type": "string",
      "description": "Concepto o motivo del gasto (no vacío)"
    },
    "monto": {
      "type": "number",
      "description": "Importe del gasto, debe ser un valor estrictamente mayor a cero"
    },
    "categoria": {
      "type": "string",
      "description": "Categoría asignada: 'comida', 'transporte', 'entretenimiento' u 'otros'"
    }
  },
  "required": ["descripcion", "monto", "categoria"]
}
```

### Respuesta de Éxito
```json
{
  "id": 14,
  "usuario_id": 1,
  "descripcion": "Metrobus mensual",
  "monto": 35.0,
  "categoria": "transporte",
  "fecha": "2026-09-19T16:20:00"
}
```

### Respuestas de Error Estructurado
```json
{
  "error": "Categoría 'tecnología' inválida. Permitidas: comida, transporte, entretenimiento, otros"
}
```
```json
{
  "error": "El gasto excede el límite máximo acumulado de 500.0 para la categoría 'transporte'"
}
```

---

## 2. Tool `listar_gastos`

### Descripción
Recupera los gastos personales del usuario autenticado en lotes paginados utilizando `skip` y `limit`.

### Parámetros de Entrada (JSON Schema)
```json
{
  "type": "object",
  "properties": {
    "skip": {
      "type": "integer",
      "default": 0,
      "description": "Cantidad de registros iniciales a omitir (offset)"
    },
    "limit": {
      "type": "integer",
      "default": 20,
      "description": "Cantidad máxima de registros a retornar (límite de página)"
    }
  }
}
```

### Respuesta de Éxito
```json
[
  {
    "id": 14,
    "usuario_id": 1,
    "descripcion": "Metrobus mensual",
    "monto": 35.0,
    "categoria": "transporte",
    "fecha": "2026-09-19T16:20:00"
  }
]
```

### Errores Estructurados
```json
{
  "error": "Parámetros de paginación inválidos (skip >= 0, limit >= 1)"
}
```
