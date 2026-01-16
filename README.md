# 🚀 Protonion Jira Agent

MCP (Model Context Protocol) server para integración de Jira con Antigravity AI.

## 📦 Instalación Rápida

### Clonar el Repositorio
```bash
git clone https://github.com/YOUR_USERNAME/jira-agent.git
cd jira-agent
```

### Instalar Dependencias
```bash
# Instalar uv (si no lo tienes)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Instalar dependencias del proyecto
uv sync
```

### Configurar Credenciales
```bash
# Crear archivo .env desde template
copy .env.example .env

# Editar con tus credenciales
notepad .env
```

Necesitas:
- `JIRA_URL`: Tu dominio de Jira (ej: `https://tuempresa.atlassian.net`)
- `JIRA_USER`: Tu email de Jira
- `JIRA_API_TOKEN`: Token de API ([Obtener aquí](https://id.atlassian.com/manage-profile/security/api-tokens))

### Configurar Antigravity

Edita: `C:\Users\<TU_USER>\.gemini\antigravity\mcp_config.json`

```json
{
  "mcpServers": {
    "jira-protonion": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\ruta\\completa\\al\\jira-agent",
        "server.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

**⚠️ Cambia la ruta a donde clonaste el proyecto**

### Verificar

```bash
# Probar el servidor
uv run server.py list

# Ejecutar tests
uv run pytest tests/ -v
```

### Reiniciar Antigravity

Cierra y abre Antigravity para cargar el servidor MCP.

---

## 🛠️ Uso

### Herramientas Disponibles

| Herramienta | Descripción |
|-------------|-------------|
| `ping` | 🩺 Health check completo |
| `list_my_tasks` | 📋 Ver tus tareas pendientes |
| `inspect_task` | 🔍 Ver detalles de una tarea |
| `safe_move_task` | 🔄 Mover tarea a nuevo estado |
| `create_task` | ✨ Crear nueva tarea |
| `search_colleague` | 👥 Buscar usuario por nombre |

### Ejemplos desde Antigravity

```
"Lista mis tareas de Jira"
"Muestra los detalles de la tarea CRM-20"
"Mueve CRM-24 a In Progress"
"Crea una tarea: Implementar autenticación OAuth"
```

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
uv run pytest tests/ -v

# Tests específicos
uv run pytest tests/test_server.py::TestValidators -v
```

---

## 📁 Estructura del Proyecto

```
jira-agent/
├── src/
│   └── jira_tools/
│       ├── client.py         # Cliente Jira
│       ├── config.py         # Configuración
│       ├── validators.py     # Validación de inputs
│       ├── cache.py          # Sistema de caching
│       └── healthcheck.py    # Health checks
├── tests/
│   └── test_server.py        # Tests unitarios
├── server.py                 # Servidor MCP principal
├── .env.example              # Template de configuración
└── pyproject.toml            # Dependencias
```

---

## 🔒 Seguridad

- ✅ `.env` está en `.gitignore` (nunca subas tus credenciales)
- ✅ Usa `.env.example` como template
- ⚠️ Rota tu API token periódicamente

---

## 📚 Documentación Adicional

- [Guía de Buenas Prácticas](.agent/MCP_REFACTORING_BEST_PRACTICES.md)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Jira API Docs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)

---

## ⚙️ Mejoras Implementadas

- ✅ **Validación de inputs** - Previene ataques injection
- ✅ **Caching TTL** - Reduce llamadas API ~50%
- ✅ **Health checks** - Monitoreo completo
- ✅ **Tests automatizados** - 13 tests passing
- ✅ **Mensajes de error claros** - Debugging más fácil

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

MIT License - Siéntete libre de usar y modificar.

---

**Hecho con ❤️ usando FastMCP y uv**
