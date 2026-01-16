
from mcp.server.fastmcp import FastMCP
import platform
import psutil
import os

mcp = FastMCP("Protonion MCP System")

@mcp.tool()
def get_system_brief() -> str:
    """💻 System Info - Get a quick overview of the current machine's health"""
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    os_info = f"{platform.system()} {platform.release()}"
    
    return (
        f"🖥️ **System Brief:**\n"
        f"- OS: {os_info}\n"
        f"- CPU Usage: {cpu}%\n"
        f"- RAM Usage: {ram}%"
    )

if __name__ == "__main__":
    mcp.run()
