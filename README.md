# 🤖 Protonion MCP Server Tools

A professional, modular, and enterprise-grade framework for building and managing portable MCP agents.

## 🚀 Features
- **Modular Architecture**: Separate agents (Jira, Admin, etc.) sharing a common core library.
- **Portable**: Designed to work across different machines with zero hardcoding.
- **Enterprise-ready**: Includes input validation, TTL caching, health checks, and a comprehensive test suite.
- **Unified Management**: Managed centrally via the Protonion MCP Manager.

---

## 📦 Quick Installation

### 1. Register the Server
Add this to your `mcp-registry.json` (managed by Protonion MCP Manager):
```json
"protonion-mcp-jira": {
    "description": "Jira Agent - Task Management",
    "directory": "protonion-mcp-server-tools",
    "repository": "https://github.com/hadevelopment/protonion-mcp-server-tools.git",
    "env_template": ".env.example",
    "env_required": ["JIRA_URL", "JIRA_USER", "JIRA_API_TOKEN"],
    "command": "uv",
    "args": ["src/agents/jira.py"],
    "enabled": true
}
```

### 2. Install Dependencies
```bash
# Using Protonion MCP Manager
python mcp-manager.py install protonion-mcp-jira
```

### 3. Configure Credentials
```bash
# Using the interactive wizard
python mcp-manager.py configure protonion-mcp-jira
```

---

## 🛠️ Unified Agents

This project exposes multiple independent MCP agents from a single codebase:

### 1. 🤖 Protonion MCP Jira
Focused on business logic and task management.
- `list_my_tasks`: 📋 View your pending tasks.
- `inspect_task`: 🔍 View task details and comments.
- `safe_move_task`: 🔄 Transition tasks with workflow validation.
- `create_task`: ✨ Create new tasks.
- `search_colleague`: 👥 Find team members by name.

### 2. 🛡️ Protonion MCP Admin
Focused on system health and configuration management.
- `health_check`: 🩺 Complete diagnostic of all system components.
- `show_environment`: ⚙️ View configuration status (masked security).

---

## 📁 Project Structure

```
protonion-mcp-server-tools/
├── src/
│   ├── core/           # Shared Core (DNA) 🧬
│   │   ├── cache.py    # TTL Caching system
│   │   ├── config.py   # Global configuration loader
│   │   ├── validators.py # Generic input validation
│   │   └── healthcheck.py # Health check engine
│   ├── services/       # API Integration Layer 🧠
│   │   └── jira_service.py # Jira API client logic
│   └── agents/         # MCP Entry Points (Agents) 🤖
│       ├── jira.py     # Jira Business Agent
│       └── admin.py    # System Admin Agent
├── tests/              # Automated Test Suite 🧪
├── README.md           # Documentation
├── pyproject.toml      # Dependency management (uv)
└── .env.example        # Configuration template
```

---

## 🧪 Testing

```bash
# Run all tests
uv run pytest tests/ -v
```

---

## 🔒 Security

- ✅ `.env` is ignored by git (never commit secrets).
- ✅ Masked sensitive data in logs and admin tools.
- ✅ Robust input sanitization in all MCP tools.

---

## 📄 License

MIT License - Feel free to use and modify.

---

**Built with ❤️ by [hadevelopment](https://github.com/hadevelopment) using FastMCP and uv**
