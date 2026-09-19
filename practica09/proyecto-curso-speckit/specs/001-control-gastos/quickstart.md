# Quickstart & Validation Guide: Sistema de Control de Gastos Personales

Guía práctica para levantar el entorno de desarrollo, ejecutar las suites de pruebas y validar manualmente los flujos completos tanto en la API REST como en el servidor MCP.

---

## 1. Prerrequisitos y Configuración del Entorno

### Dependencias del Sistema
- Python 3.11+
- Git

### Creación del Entorno Virtual e Instalación
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install fastapi "uvicorn[standard]" "sqlalchemy>=2.0" alembic pyjwt "passlib[bcrypt]" "bcrypt>=4.0.1,<4.1.0" pydantic-settings email-validator python-multipart mcp httpx pytest pytest-cov
```

### Configuración de Variables de Entorno (`.env`)
Crear un archivo `.env` en la raíz del proyecto basado en `.env.example`:
```bash
cp .env.example .env
```
Contenido esperado de `.env`:
```ini
SECRET_KEY=clave_criptografica_segura_generada_aleatoriamente_32_bytes
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./gastos.db
DEMO_USER_EMAIL=demo@gastos.local
```

---

## 2. Inicialización de Persistencia y Migraciones

```bash
# Inicializar y aplicar migraciones con Alembic
alembic upgrade head
```

---

## 3. Ejecución de la Suite de Pruebas y Cobertura

Para validar automáticamente todos los contratos y verificar los umbrales constitucionales de cobertura (Artículo VII.3):

```bash
# Ejecutar suite completa con reporte de cobertura
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

### Comprobaciones Específicas por Capa:
```bash
# Pruebas Unitarias de Lógica de Negocio (sin mocks, inyectando RepositorioFalso)
pytest tests/unit/

# Pruebas de Integración con SQLite en memoria
pytest tests/integration/

# Pruebas de Endpoints de la API y MCP
pytest tests/api/
```

---

## 4. Validación Manual del Flujo E2E (API REST)

Iniciar el servidor de desarrollo:
```bash
uvicorn app.main:app --reload --port 8000
```

### Paso 1: Registrar un Usuario
```bash
curl -X POST http://localhost:8000/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{"email": "usuario1@test.com", "password": "Password123!"}'
# Esperado: HTTP 201 Created con {"id": 1, "email": "usuario1@test.com"}
```

### Paso 2: Obtener Token de Acceso
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/usuarios/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=usuario1@test.com&password=Password123!" | jq -r .access_token)

echo "Token obtenido: $TOKEN"
```

### Paso 3: Registrar un Gasto Válido
```bash
curl -X POST http://localhost:8000/gastos/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"descripcion": "Supermercado semanal", "monto": 120.0, "categoria": "comida"}'
# Esperado: HTTP 201 con el gasto creado y monto 120.0
```

### Paso 4: Validar Error de Categoría Inválida
```bash
curl -i -X POST http://localhost:8000/gastos/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"descripcion": "Pasaje avión", "monto": 200.0, "categoria": "viajes"}'
# Esperado: HTTP 400 Bad Request con detalle de categoría inválida
```

### Paso 5: Validar Límite Acumulado Excedido (500.0)
```bash
curl -i -X POST http://localhost:8000/gastos/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"descripcion": "Banquete", "monto": 400.0, "categoria": "comida"}'
# Esperado: HTTP 400 Bad Request (120.0 + 400.0 = 520.0 > 500.0)
```

### Paso 6: Listar Gastos Propios
```bash
curl -X GET "http://localhost:8000/gastos/?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN"
# Esperado: HTTP 200 OK con la lista de gastos del usuario1
```

---

## 5. Validación de Tools MCP

El servidor MCP expone las herramientas `registrar_gasto` y `listar_gastos` montadas sobre `/mcp`.

1. Conectar cualquier cliente MCP compatible configurando el transporte `streamable-http` apuntando a `http://localhost:8000/mcp` con header `Authorization: Bearer <token>`.
2. Para inspección local vía `stdio`:
   ```bash
   python -m app.mcp.server
   ```
   (En modo stdio se empleará el `DEMO_USER_EMAIL` configurado en `.env`).
