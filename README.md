# 🤖 Protonion MCP Server Tools

A robust, enterprise-grade framework for portable MCP agents. Currently featuring the **Protonion Jira Agent**.

## 🚀 Features
- **Standalone Architecture**: The entire Jira agent lives in a single, portable `jira.py` file with zero complex dependencies.
- **Auto-Configurable**: Includes built-in tools (`update_config`) to set credentials directly from the AI Interface (Antigravity).
- **Protonion Framework**: Integrated with the MCP Manager for one-click installation and updates.
- **Enterprise-ready**: Includes input validation, workflow enforcement, and team collaboration tools.

---

## 📦 Quick Installation

### 1. Using Protonion MCP Manager (Recommended)
This repository includes the `mcp-manager.py` utility which automates the setup.

```bash
# 1. Install/Update the agent
python mcp-manager.py install-all

# 2. Restart your AI Editor (Antigravity/Cursor)
```

### 2. Manual Setup
If you prefer manual configuration, simply run the agent using `uv`:

```bash
uv run jira.py
```

---

## 🛠️ Included Agents

### 🤖 Protonion Jira (`jira.py`)
A comprehensive Jira integration that creates a professional "App-like" experience within your AI editor.

**Tools:**
- `list_my_tasks`: 📋 View your pending tasks instantly.
- `inspect_task`: 🔍 View rich details, description, and comments of any task.
- `safe_move_task`: 🔄 Transition tasks (e.g., To Do -> Done) with workflow validation.
- `create_task`: ✨ Create new tasks from natural language.
- `search_colleague`: 👥 Find team members by name to assign tasks.
- `show_config` / `update_config`: ⚙️ View and update credentials directly from the UI.

---

## 📁 Project Structure

```
protonion-mcp-server-tools/
├── jira.py             # 🌟 MAIN AGENT: Standalone Jira MCP Server
├── mcp-manager.py      # 🛠️ UTILITY: Manager for installation/updates
├── src/                # (Legacy/Dev) Modular source code (optional)
├── tests/              # Automated Test Suite
├── README.md           # Documentation
├── pyproject.toml      # Dependency management (uv)
└── .env.example        # Configuration template
```

---

## 🔒 Security & Configuration

1.  **Credentials**: Never committed to Git. Stored locally in a `.env` file next to the agent.
2.  **Management**: You can update your API Token or URL using the `update_config` tool inside the agent.
3.  **Masking**: Sensitive data is masked in logs and configuration views.

---

## 📄 License

MIT License - Feel free to use and modify.

---

**Built with ❤️ by [hadevelopment](https://github.com/hadevelopment) using FastMCP and uv**
