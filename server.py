
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv

# 1. Cargar configuración global
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# 2. Inicializar el Servidor MCP Universal
mcp = FastMCP("Protonion Multi-tool Agent")

# 3. Registro de Módulos de Herramientas
# Importamos los registradores de cada servicio
from src.mcp_tools.admin import register_admin_tools
from src.mcp_tools.jira import register_jira_tools
# Ejemplo futuro: from src.mcp_tools.github import register_github_tools

# 4. Activar herramientas por servicio
register_admin_tools(mcp)  # Herramientas de sistema y config
register_jira_tools(mcp)   # Herramientas de Jira
# register_github_tools(mcp) # Solo tendrías que descomentar esto mañana

if __name__ == "__main__":
    mcp.run()
