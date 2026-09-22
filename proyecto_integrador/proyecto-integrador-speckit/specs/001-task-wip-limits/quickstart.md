# Guía de Inicio Rápido y Validación: Sistema de Gestión de Tareas

**Feature**: `001-task-wip-limits` | **Fecha**: 2026-09-21

Esta guía describe los pasos necesarios para configurar el entorno de ejecución, ejecutar las migraciones, levantar la API REST y el servidor MCP, y verificar el cumplimiento de todas las reglas de negocio y cobertura de pruebas.

---

## 1. Requisitos Previos e Instalación

### 1.1 Clonar o situarse en el repositorio
```bash
cd /home/edgar/Documentos/CURSO\ IA/CURSO\ 2/semana1/practica1/curso-mcp-edgar/proyecto_integrador/proyecto-integrador-speckit
```

### 1.2 Crear y activar entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 1.3 Instalar dependencias
```bash
pip install -r requirements.txt
```
*(Asegurándose de que `passlib[bcrypt]` y `bcrypt<4.1` estén instalados).*

### 1.4 Configurar Variables de Entorno
Copiar el archivo de ejemplo y configurar las credenciales:
```bash
cp .env.example .env
```
Contenido base de `.env`:
```env
DATABASE_URL=sqlite:///./tareas.db
SECRET_KEY=clave_secreta_super_segura_para_desarrollo_local_12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
MCP_USER_EMAIL=usuario@ejemplo.com
```

---

## 2. Inicialización de Base de Datos y Migraciones

Ejecutar las migraciones con Alembic o inicializar la base de datos SQLite:
```bash
alembic upgrade head
```

---

## 3. Ejecución de la Suite de Pruebas y Cobertura

Para validar que el 100% de las reglas de negocio y los umbrales constitucionales se cumplen:

### 3.1 Ejecutar todos los tests
```bash
pytest -v
```

### 3.2 Reporte de Cobertura Constitucional (Artículo VII.3)
```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=70
```
*Criterios de aprobación requeridos:*
- $\ge 90\%$ de cobertura de líneas en `app/services/`
- $\ge 70\%$ de cobertura global combinada (omitiendo `main.py`, `mcp/*`, y `logging_config.py`).

---

## 4. Ejecución de Servidores

### 4.1 Iniciar FastAPI (REST API + MCP Streamable HTTP)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Documentación interactiva Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Endpoint MCP SSE / Streamable: [http://localhost:8000/mcp](http://localhost:8000/mcp)

### 4.2 Iniciar Servidor MCP en modo `stdio` (para Claude Desktop / Antigravity)
```bash
python -m app.mcp.server
```

---

## 5. Escenarios de Validación Rápida (End-to-End con cURL)

### Escenario 1: Registro e Inicio de Sesión
```bash
# 1. Registrar usuario
curl -X POST http://localhost:8000/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{"email": "edgar@ejemplo.com", "password": "passwordSeguro123"}'

# 2. Obtener Token JWT
TOKEN=$(curl -s -X POST http://localhost:8000/usuarios/token \
  -d "username=edgar@ejemplo.com&password=passwordSeguro123" | jq -r .access_token)

echo "Token obtenido: $TOKEN"
```

### Escenario 2: Límite de Prioridad Alta (Máx 2 abiertas)
```bash
# Crear tarea 1 (Prioridad Alta) -> 201 Created
curl -X POST http://localhost:8000/tareas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Tarea Crítica 1", "prioridad": "alta"}'

# Crear tarea 2 (Prioridad Alta) -> 201 Created
curl -X POST http://localhost:8000/tareas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Tarea Crítica 2", "prioridad": "alta"}'

# Crear tarea 3 (Prioridad Alta) -> 400 Bad Request (LimitePrioridadAltaExcedidoError)
curl -X POST http://localhost:8000/tareas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Tarea Crítica 3", "prioridad": "alta"}'
```

### Escenario 3: Límite WIP (Máx 3 en progreso) y Transición Inválida
```bash
# Intentar pasar tarea de pendiente directo a completada -> 400 Bad Request (TransicionEstadoInvalidaError)
curl -X PATCH http://localhost:8000/tareas/1/estado \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"estado": "completada"}'

# Mover a en_progreso válidamente
curl -X PATCH http://localhost:8000/tareas/1/estado \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"estado": "en_progreso"}'
```
