# Contrato de Herramientas MCP: Sistema de Gestión de Tareas

**Feature**: `001-task-wip-limits` | **Versión**: 1.0.0

Este documento define la especificación del protocolo Model Context Protocol (MCP) conforme al **Artículo VI** de la Constitución.

---

## Directrices Constitucionales MCP (Artículo VI)

1. **Reutilización de Services**: Cada tool MCP delega directamente en funciones de `app/services/tareas_service.py`. No existe lógica de negocio duplicada en la capa MCP.
2. **Descripciones Accionables**: Descripciones concisas y orientadas a la toma de decisiones de agentes de inteligencia artificial.
3. **Manejo de Errores Estructurados**: Toda excepción de negocio se captura y retorna como un objeto JSON `{"error": "<NombreExcepcion>: <Detalle>"}`, garantizando que la conexión o sesión MCP nunca se rompa ante un error de validación o capacidad.
4. **Resolución de Identidad**:
   - **Transporte HTTP Streamable / SSE**: Se extrae el token JWT de la sesión y se resuelve el `usuario_id` autenticado.
   - **Transporte `stdio`**: La identidad se resuelve a partir de la variable de entorno `MCP_USER_EMAIL` (con fallback documentado a un usuario de prueba en base de datos).

---

## 1. Tool: `crear_tarea`

### Descripción
"Crea una nueva tarea personal validando el límite de un máximo de 2 tareas de prioridad alta abiertas simultáneamente."

### Parámetros de Entrada (`inputSchema`)
```json
{
  "type": "object",
  "properties": {
    "titulo": {
      "type": "string",
      "description": "Título breve y descriptivo de la tarea (no vacío)."
    },
    "prioridad": {
      "type": "string",
      "enum": ["baja", "media", "alta"],
      "description": "Nivel de prioridad de la tarea."
    },
    "descripcion": {
      "type": "string",
      "description": "Detalles adicionales u observaciones de la tarea (opcional)."
    }
  },
  "required": ["titulo", "prioridad"]
}
```

### Respuestas
- **Éxito**:
  ```json
  {
    "success": true,
    "tarea": {
      "id": 15,
      "titulo": "Preparar informe trimestral",
      "prioridad": "alta",
      "estado": "pendiente",
      "descripcion": "Incluir métricas de satisfacción",
      "creado_en": "2026-09-21T21:30:00Z"
    }
  }
  ```
- **Error de Negocio (Límite Excedido)**:
  ```json
  {
    "error": "LimitePrioridadAltaExcedidoError: No se pueden tener más de 2 tareas de prioridad alta abiertas simultáneamente"
  }
  ```

---

## 2. Tool: `listar_tareas`

### Descripción
"Lista las tareas personales del usuario autenticado ordenadas de forma descendente por fecha de creación, con paginación y filtro opcional por estado."

### Parámetros de Entrada (`inputSchema`)
```json
{
  "type": "object",
  "properties": {
    "skip": {
      "type": "integer",
      "default": 0,
      "description": "Número de registros a omitir para paginación."
    },
    "limit": {
      "type": "integer",
      "default": 20,
      "description": "Cantidad máxima de tareas a retornar (máximo 100)."
    },
    "estado": {
      "type": "string",
      "enum": ["pendiente", "en_progreso", "completada"],
      "description": "Filtro opcional por estado de la tarea."
    }
  }
}
```

### Respuestas
- **Éxito**:
  ```json
  {
    "success": true,
    "total": 1,
    "tareas": [
      {
        "id": 15,
        "titulo": "Preparar informe trimestral",
        "prioridad": "alta",
        "estado": "pendiente",
        "descripcion": "Incluir métricas de satisfacción",
        "creado_en": "2026-09-21T21:30:00Z"
      }
    ]
  }
  ```

---

## 3. Tool: `iniciar_tarea_prioritaria`

### Descripción
"Busca la tarea en estado 'pendiente' con mayor prioridad ('alta' > 'media' > 'baja') del usuario y la transiciona a 'en_progreso', validando que no se exceda el límite WIP de 3 tareas en progreso."

### Parámetros de Entrada (`inputSchema`)
```json
{
  "type": "object",
  "properties": {}
}
```

### Respuestas
- **Éxito**:
  ```json
  {
    "success": true,
    "mensaje": "Tarea iniciada correctamente",
    "tarea": {
      "id": 15,
      "titulo": "Preparar informe trimestral",
      "prioridad": "alta",
      "estado": "en_progreso",
      "actualizado_en": "2026-09-21T21:35:00Z"
    }
  }
  ```
- **Sin tareas pendientes**:
  ```json
  {
    "success": false,
    "mensaje": "No hay tareas pendientes disponibles para iniciar"
  }
  ```
- **Error de Negocio (Límite WIP Excedido)**:
  ```json
  {
    "error": "LimiteWIPExcedidoError: No se pueden tener más de 3 tareas en progreso simultáneamente"
  }
  ```
