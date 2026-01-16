# 🏗️ MCP Server Refactoring - Best Practices Guide

## 📚 **Tabla de Contenidos**

1. [Arquitectura y Diseño](#arquitectura-y-diseño)
2. [Diseño de Herramientas (Tools)](#diseño-de-herramientas-tools)
3. [Manejo de Errores y Validación](#manejo-de-errores-y-validación)
4. [Código Limpio y Patrones](#código-limpio-y-patrones)
5. [Testing y Debugging](#testing-y-debugging)
6. [Performance y Escalabilidad](#performance-y-escalabilidad)
7. [Seguridad](#seguridad)
8. [Producción y Deployment](#producción-y-deployment)

---

## 🏛️ **Arquitectura y Diseño**

### **Principio de Responsabilidad Única (Single Responsibility)**
- ✅ Cada servidor MCP debe modelarse alrededor de un **único dominio** (negocio o técnico)
- ✅ Las herramientas dentro del servidor deben ser **cohesivas** y relevantes a ese dominio
- ✅ **Ejemplo**: Un servidor de Jira no debe manejar integraciones de GitHub

```python
# ❌ MAL - Servidor con responsabilidades mixtas
@mcp.tool()
def jira_create_task(...): pass

@mcp.tool()
def github_create_pr(...): pass  # Pertenece a otro servidor

# ✅ BIEN - Servidor enfocado
@mcp.tool()
def create_task(...): pass

@mcp.tool()
def move_task(...): pass

@mcp.tool()
def list_my_tasks(...): pass
```

### **Separación de Concerns (Layered Architecture)**

```
┌─────────────────────────────────┐
│   server.py (MCP Layer)         │  ← Decoradores @mcp.tool()
├─────────────────────────────────┤
│   client.py (Service Layer)     │  ← Lógica de negocio
├─────────────────────────────────┤
│   models.py (Domain Layer)      │  ← Modelos de datos
├─────────────────────────────────┤
│   config.py (Config Layer)      │  ← Configuración
└─────────────────────────────────┘
```

**Refactorización recomendada:**

```python
# ❌ MAL - Todo mezclado en server.py
@mcp.tool()
def inspect_task(issue_key: str):
    jira = JIRA(server=os.getenv("JIRA_URL"), ...)  # Config mezclado
    issue = jira.issue(issue_key)  # Cliente mezclado
    return f"{issue.key}: {issue.fields.summary}"  # Formato mezclado

# ✅ BIEN - Separación clara
@mcp.tool()
def inspect_task(issue_key: str):
    client = get_client()  # Inyección de dependencia
    digest = client.get_issue_digest(issue_key)  # Service layer
    return format_issue_digest(digest)  # Formatting layer
```

---

## 🛠️ **Diseño de Herramientas (Tools)**

### **Diseño Basado en Intenciones (Intent-Based)**

```python
# ❌ MAL - Mapeo directo a endpoints
@mcp.tool()
def jira_api_issue_transition_post(issue_id, transition_id): pass

# ✅ BIEN - Basado en intención del usuario
@mcp.tool()
def move_task(issue_key: str, target_status: str): pass
```

### **Descripciones Claras y Accionables**

```python
# ❌ MAL - Descripción técnica
@mcp.tool()
def transition_issue(key, status):
    """Transitions a JIRA issue to a new status."""
    pass

# ✅ BIEN - Descripción orientada a UX
@mcp.tool()
def safe_move_task(issue_key: str, target_status: str, comment: Optional[str] = None):
    """🔄 Move Task - Transition a task to a new status (e.g., 'In Progress', 'Done') 
    with workflow validation and optional comment"""
    pass
```

### **Operaciones Atómicas y Autocontenidas**

```python
# ✅ BIEN - Cada llamada es autoc ontenida
@mcp.tool()
def list_my_tasks(board_id: int = 67):
    """Establece conexión, consulta, y retorna resultados en una sola llamada"""
    client = get_client()  # Nueva conexión por call
    return client.get_board_issues(board_id)
```

**Beneficios:**
- ✅ Mejor usabilidad
- ✅ Mayor confiabilidad
- ✅ No requiere estado global

---

## ⚠️ **Manejo de Errores y Validación**

### **Modelo de Errores en 3 Capas**

```python
# 1. Errores de Transporte (manejados por la librería)
#    - Timeouts de red
#    - Fallos de autenticación

# 2. Errores de Protocolo (manejados por MCP/FastMCP)
#    - JSON-RPC violations
#    - Requests malformadas

# 3. Errores de Aplicación (TU RESPONSABILIDAD)
@mcp.tool()
def safe_move_task(issue_key: str, target_status: str):
    try:
        result = client.safe_transition(issue_key, target_status)
        
        if not result["success"]:
            # ✅ Error semántico para autocorrección del LLM
            return (
                f"⛔ BLOCKER: {result['message']}\n"
                f"💡 Valid transitions: {result.get('valid_transitions', [])}"
            )
        
        return f"✅ {result['message']}"
    
    except Exception as e:
        # ✅ Error técnico para debugging
        return f"System Error: {str(e)}"
```

### **Mensajes de Error Accionables**

```python
# ❌ MAL - Error vago
return "Error: Task not found"

# ✅ BIEN - Error con contexto y solución
return (
    f"⛔ Task {issue_key} not found.\n"
    f"💡 Tip: Use 'list_my_tasks' to see available tasks."
)
```

### **Validación de Inputs**

```python
@mcp.tool()
def inspect_task(issue_key: str):
    # ✅ Validación temprana
    if not issue_key or not isinstance(issue_key, str):
        return "⛔ Invalid issue_key. Expected format: 'CRM-123'"
    
    if not re.match(r'^[A-Z]+-\d+$', issue_key):
        return f"⛔ Issue key '{issue_key}' has invalid format. Expected: PROJECT-NUMBER"
    
    try:
        client = get_client()
        return client.get_issue_digest(issue_key)
    except Exception as e:
        return f"System Error: {str(e)}"
```

---

## 🧹 **Código Limpio y Patrones**

### **Refactorización de Condicionales Complejas**

```python
# ❌ MAL - Condicionales anidadas
def process_issue(issue):
    if issue:
        if issue.status:
            if issue.status == "Done":
                return "✅ Complete"
            else:
                return "🔄 In Progress"
        else:
            return "⚠️ No status"
    else:
        return "❌ No issue"

# ✅ BIEN - Guard clauses
def process_issue(issue):
    if not issue:
        return "❌ No issue"
    
    if not issue.status:
        return "⚠️ No status"
    
    if issue.status == "Done":
        return "✅ Complete"
    
    return "🔄 In Progress"
```

### **Evitar Hardcoding**

```python
# ❌ MAL
@mcp.tool()
def list_my_tasks():
    jql = "assignee = currentUser() AND statusCategory != Done"
    board_id = 67  # Hardcoded!
    
# ✅ BIEN
class JiraConfig:
    DEFAULT_BOARD_ID = int(os.getenv("JIRA_BOARD_ID", "67"))
    JQL_MY_PENDING = "assignee = currentUser() AND statusCategory != Done"

@mcp.tool()
def list_my_tasks(board_id: int = JiraConfig.DEFAULT_BOARD_ID):
    jql = JiraConfig.JQL_MY_PENDING
```

### **Generators para Grandes Datasets**

```python
# ❌ MAL - Carga todo en memoria
def get_all_issues():
    issues = []
    for page in range(100):
        issues.extend(client.get_page(page))
    return issues

# ✅ BIEN - Usa generator
def get_all_issues():
    for page in range(100):
        yield from client.get_page(page)
```

### **Modularización**

```python
# Antes (server.py = 500 líneas)
# server.py
@mcp.tool()
def ping(): ...
@mcp.tool()
def list_my_tasks(): ...
@mcp.tool()
def inspect_task(): ...
# ... 20 más

# ✅ Después (refactorizado)
# server.py (50 líneas)
from tools.healthcheck import ping
from tools.tasks import list_my_tasks, inspect_task, create_task
from tools.workflow import safe_move_task
from tools.users import search_colleague

# tools/tasks.py
def list_my_tasks(): ...
def inspect_task(): ...
def create_task(): ...
```

---

## 🧪 **Testing y Debugging**

### **Testing en Memoria (FastMCP)**

```python
# tests/test_server.py
import pytest
from mcp.client import ClientSession
from server import mcp

@pytest.mark.asyncio
async def test_ping():
    async with mcp.test_client() as client:
        result = await client.call_tool("ping", {})
        assert result == "🚀 Protonion Agent Online & Ready"

@pytest.mark.asyncio
async def test_list_tasks_empty():
    async with mcp.test_client() as client:
        result = await client.call_tool("list_my_tasks", {"board_id": 999})
        assert "No pending tasks" in result
```

### **Testing End-to-End**

```python
# tests/test_integration.py
def test_full_workflow():
    """Test: create task → move to in progress → complete"""
    # 1. Create
    result = create_task("Test task", "Description")
    assert "Created task" in result
    key = extract_key(result)
    
    # 2. Move
    result = safe_move_task(key, "In Progress")
    assert "✅" in result
    
    # 3. Verify
    result = inspect_task(key)
    assert "In Progress" in result
```

### **Debugging con MCP Inspector**

```bash
# Terminal
npx @modelcontextprotocol/inspector uv run server.py
```

Esto abre una interfaz web para:
- ✅ Ver tools disponibles
- ✅ Ejecutar tools con inputs
- ✅ Ver respuestas y errores
- ✅ Debugging interactivo

---

## ⚡ **Performance y Escalabilidad**

### **Async/Await para I/O-Bound Operations**

```python
# ❌ MAL - Bloqueante
def get_multiple_issues(keys):
    results = []
    for key in keys:
        results.append(client.get_issue(key))  # Secuencial
    return results

# ✅ BIEN - Concurrente
async def get_multiple_issues(keys):
    tasks = [client.get_issue_async(key) for key in keys]
    return await asyncio.gather(*tasks)  # Paralelo
```

### **Caching de Resultados Frecuentes**

```python
from functools import lru_cache

# ✅ Cache de configuración
@lru_cache(maxsize=1)
def get_client():
    return JiraClient()

# ✅ Cache TTL para datos
from cachetools import TTLCache
cache = TTLCache(maxsize=100, ttl=300)  # 5 minutos

def get_user_info(account_id):
    if account_id in cache:
        return cache[account_id]
    
    user = client.fetch_user(account_id)
    cache[account_id] = user
    return user
```

### **Paginación para Grandes Listas**

```python
# ✅ BIEN
@mcp.tool()
def list_my_tasks(board_id: int = 67, limit: int = 10, offset: int = 0):
    """📋 My Tasks - Supports  pagination"""
    client = get_client()
    issues = client.get_board_issues(
        board_id=board_id,
        limit=limit,
        offset=offset
    )
    return format_tasks(issues, limit, offset)
```

---

## 🔒 **Seguridad**

### **Sanitización de Inputs**

```python
import re

def sanitize_issue_key(key: str) -> str:
    """Previene injection attacks"""
    # Solo permite PROJECT-NUMBER
    if not re.match(r'^[A-Z]{1,10}-\d{1,10}$', key):
        raise ValueError(f"Invalid issue key format: {key}")
    return key

@mcp.tool()
def inspect_task(issue_key: str):
    safe_key = sanitize_issue_key(issue_key)
    return client.get_issue(safe_key)
```

### **No Exponer Secretos en Logs**

```python
# ❌ MAL
def get_client():
    api_token = os.getenv("JIRA_API_TOKEN")
    logger.info(f"Connecting with token: {api_token}")  # ¡NUNCA!
    
# ✅ BIEN
def get_client():
    api_token = os.getenv("JIRA_API_TOKEN")
    logger.info(f"Connecting to Jira (token: ***{api_token[-4:]})")
```

### **Validación de Permisos**

```python
@mcp.tool()
def delete_task(issue_key: str):
    client = get_client()
    
    # ✅ Verificar permisos antes de actuar
    if not client.user_can_delete(issue_key):
        return "⛔ Permission Denied: You cannot delete this task"
    
    return client.delete_issue(issue_key)
```

---

## 🚀 **Producción y Deployment**

### **Configuración por Entorno**

```python
# config.py
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"

class Config:
    ENV = Environment(os.getenv("ENV", "dev"))
    
    # URLs por entorno
    JIRA_URLS = {
        Environment.DEVELOPMENT: "https://dev.atlassian.net",
        Environment.STAGING: "https://staging.atlassian.net",
        Environment.PRODUCTION: "https://prod.atlassian.net",
    }
    
    @property
    def jira_url(self):
        return self.JIRA_URLS[self.ENV]
```

### **Health Checks**

```python
@mcp.tool()
def healthcheck():
    """🩺 Health Check - Verifies all dependencies"""
    checks = {}
    
    # 1. Config
    checks["config"] = JiraConfig.is_configured()
    
    # 2. API Connectivity
    try:
        client = get_client()
        client.server_info()
        checks["api"] = True
    except:
        checks["api"] = False
    
    # 3. Auth
    try:
        client.current_user()
        checks["auth"] = True
    except:
        checks["auth"] = False
    
    status = "✅" if all(checks.values()) else "⛔"
    return f"{status} Health: {json.dumps(checks, indent=2)}"
```

### **Logging Estructurado**

```python
import logging
import json

# ✅ Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@mcp.tool()
def list_my_tasks(board_id: int):
    logger.info(f"Tool called", extra={
        "tool": "list_my_tasks",
        "board_id": board_id,
        "user": get_current_user()
    })
    
    try:
        result = client.get_tasks(board_id)
        logger.info(f"Success", extra={"task_count": len(result)})
        return result
    except Exception as e:
        logger.error(f"Error", extra={"error": str(e)}, exc_info=True)
        raise
```

---

## 📋 **Checklist de Refactorización**

### **Phase 1: Estructura**
- [ ] Separar concerns en módulos (client, models, config, tools)
- [ ] Crear estructura de directorios clara
- [ ] Mover configuración a variables de entorno

### **Phase 2: Herramientas**
- [ ] Revisar descripciones para que sean user-friendly
- [ ] Agregar emojis contextuales
- [ ] Validar que sean atómicas y autocontenidas

### **Phase 3: Errores**
- [ ] Implementar modelo de 3 capas
- [ ] Agregar mensajes accionables
- [ ] Validar inputs tempranamente

### **Phase 4: Testing**
- [ ] Crear tests unitarios para cada tool
- [ ] Agregar tests de integración
- [ ] Configurar MCP Inspector para debugging

### **Phase 5: Performance**
- [ ] Identificar operaciones I/O-bound para async
- [ ] Implementar caching donde aplique
- [ ] Agregar paginación a listas grandes

### **Phase 6: Producción**
- [ ] Configurar logging estructurado
- [ ] Implementar healthchecks
- [ ] Crear documentación de deployment

---

## 🎯 **Próximos Pasos Recomendados para Protonion**

1. **Refactorizar `server.py`**:
   - Mover tools a módulos separados (`tools/`)
   - Extraer lógica de cliente a `client.py`

2. **Mejorar Manejo de Errores**:
   - Implementar excepciones custom
   - Agregar validación robusta

3. **Agregar Testing**:
   - Configurar pytest
   - Crear suite de tests

4. **Performance**:
   - Implementar caching para usuarios
   - Async para operaciones de red

5. **Documentación**:
   - Crear README con ejemplos
   - Documentar todos los tools

---

**Referencias**:
- [MCP Specification](https://modelcontextprotocol.io)
- [FastMCP Documentation](https://jlowin.github.io/fastmcp)
- [Clean Architecture for AI Agents](https://medium.com)
