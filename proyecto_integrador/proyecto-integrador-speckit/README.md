# Instrucciones de Ejecución — Proyecto Integrador

Sistema de Gestión de Tareas Personales con Límite de Capacidad (WIP Limits)  
**Autor:** Edgar Manuel Macas Loja

---

## 🚀 Requisitos Previos

* **Python 3.12**
* **uv** (gestor de paquetes y entornos)
* **Node.js y npx** (para inspección visual con MCP Inspector)

---

## 🛠️ Instalación y Configuración con `uv`

### 1. Posicionarse en el proyecto:
```bash
cd proyecto_integrador/proyecto-integrador-speckit
```

### 2. Configurar entorno virtual e instalar dependencias:
```bash
uv venv
source venv/bin/activate  # En Linux/macOS
uv pip install -r requirements.txt
```

### 3. Configurar variables de entorno y migraciones:
```bash
cp .env.example .env
uv run alembic upgrade head
```

---

## 🧪 Ejecución de Pruebas y Cobertura

Para correr las 92 pruebas automatizadas y verificar el cumplimiento de los umbrales de cobertura constitucional (servicios $\ge 90\%$ y global $\ge 70\%$):

```bash
uv run pytest --cov=app --cov-report=term-missing -v
```

---

## 🌐 Levantar Servidor REST y Swagger UI

Para iniciar la API REST:
```bash
uv run uvicorn app.main:app --reload
```

* **API Base:** `http://127.0.0.1:8000`
* **Swagger UI interactivo:** `http://127.0.0.1:8000/docs`
* **ReDoc:** `http://127.0.0.1:8000/redoc`
* **Health Check:** `http://127.0.0.1:8000/health`

---

## 🤖 Levantar Servidor MCP (Model Context Protocol)

### Opción 1: Inspección visual en navegador con MCP Inspector
```bash
PYTHONPATH=. npx @modelcontextprotocol/inspector uv run python -m app.mcp.server
```
1. Abre en tu navegador la URL que muestra la terminal (ejemplo: `http://localhost:5173`).
2. Verifica que el transporte seleccionado sea **STDIO** y haz clic en **Connect**.
3. Dirígete a la pestaña **Tools** para listar y ejecutar en vivo:
   * `crear_tarea`
   * `iniciar_tarea_prioritaria`
   * `listar_tareas`

### Opción 2: Prueba rápida directa por consola
```bash
uv run python -c "from app.mcp.tools import mcp_crear_tarea, mcp_listar_tareas, mcp_iniciar_tarea_prioritaria; print(mcp_crear_tarea('Preparar Informe', 'alta')); print(mcp_iniciar_tarea_prioritaria()); print(mcp_listar_tareas())"
```
