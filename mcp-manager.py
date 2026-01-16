#!/usr/bin/env python3
"""
Protonion MCP Manager - Gestiona todos tus servidores MCP
Instalación, actualización y configuración centralizada
"""
import json
import os
import subprocess
import sys
from pathlib import Path


REGISTRY_PATH = Path.home() / ".protonion" / "mcp-registry.json"
SERVERS_DIR = Path.home() / ".protonion" / "servers"
ANTIGRAVITY_CONFIG = Path.home() / ".gemini" / "antigravity" / "mcp_config.json"


def load_registry():
    """Cargar el registro de servidores MCP"""
    if not REGISTRY_PATH.exists():
        print(f"❌ Registry not found: {REGISTRY_PATH}")
        print("   Creating default registry...")
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        default_registry = {
            "version": "1.0",
            "servers": {}
        }
        
        REGISTRY_PATH.write_text(json.dumps(default_registry, indent=2))
        print(f"✅ Created: {REGISTRY_PATH}")
        return default_registry
    
    return json.loads(REGISTRY_PATH.read_text())


def save_registry(registry):
    """Guardar el registro de servidores MCP"""
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2))


def run_command(cmd, cwd=None):
    """Ejecutar comando y retornar resultado"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def install_server(name, config):
    """Instalar un servidor MCP"""
    print(f"\n{'='*60}")
    print(f"📦 Installing: {name}")
    print(f"   {config.get('description', 'No description')}")
    print(f"{'='*60}")
    
    server_dir = SERVERS_DIR / config['directory']
    
    # 1. Clonar repositorio (solo si no existe)
    if server_dir.exists():
        print(f"ℹ️  Directory already exists (shared or installed): {server_dir}")
        # Si ya existe, solo nos aseguramos de que esté actualizado
        print("   Checking for updates...")
        update_server(name, config)
    else:
        print(f"\n[1/4] Cloning repository...")
        SERVERS_DIR.mkdir(parents=True, exist_ok=True)
        
        success, output = run_command(
            f'git clone {config["repository"]} {server_dir}'
        )
        
        if not success:
            print(f"❌ Failed to clone: {output}")
            return False
        
        print(f"✅ Cloned to: {server_dir}")
    
    # 2. Instalar dependencias
    print(f"\n[2/4] Installing dependencies...")
    success, output = run_command("uv sync", cwd=server_dir)
    
    if not success:
        print(f"⚠️  Warning: {output}")
    else:
        print("✅ Dependencies installed")
    
    # 3. Configurar .env
    print(f"\n[3/4] Setting up environment...")
    env_template = server_dir / config.get('env_template', '.env.example')
    env_file = server_dir / '.env'
    
    if env_template.exists() and not env_file.exists():
        import shutil
        shutil.copy(env_template, env_file)
        print(f"✅ Created .env from template")
        
        if config.get('env_required'):
            print(f"\n⚠️  Please configure these environment variables:")
            for var in config['env_required']:
                print(f"   - {var}")
            print(f"\n   Edit: {env_file}")
            input("\n   Press Enter when ready...")
    
    # 4. Ejecutar tests (opcional)
    print(f"\n[4/4] Running tests...")
    success, output = run_command("uv run pytest tests/ -q", cwd=server_dir)
    
    if success:
        print("✅ Tests passed")
    else:
        print("⚠️  Tests failed or not available")
    
    print(f"\n✅ {name} installed successfully!")
    return True


def update_server(name, config):
    """Actualizar un servidor MCP"""
    print(f"\n🔄 Updating: {name}")
    
    server_dir = SERVERS_DIR / config['directory']
    
    if not server_dir.exists():
        print(f"❌ Server not installed: {name}")
        return False
    
    # Git Fetch & Reset (Nuclear update)
    print("Fetching and resetting to origin/main...")
    success, output = run_command("git fetch origin && git reset --hard origin/main", cwd=server_dir)
    
    if not success:
        print(f"❌ Failed to update: {output}")
        return False
    
    # Update dependencies
    print("Updating dependencies...")
    run_command("uv sync", cwd=server_dir)
    
    print(f"✅ {name} updated and synced!")
    return True


def configure_antigravity():
    """Configurar Antigravity con todos los servidores"""
    print(f"\n{'='*60}")
    print("⚙️  Configuring Antigravity...")
    print(f"{'='*60}")
    
    registry = load_registry()
    
    # Cargar config existente o crear nueva
    ANTIGRAVITY_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    
    if ANTIGRAVITY_CONFIG.exists():
        mcp_config = json.loads(ANTIGRAVITY_CONFIG.read_text())
    else:
        mcp_config = {"mcpServers": {}}
    
    # Agregar cada servidor
    for name, config in registry['servers'].items():
        if not config.get('enabled', True):
            continue
        
        server_dir = SERVERS_DIR / config['directory']
        
        if not server_dir.exists():
            print(f"⚠️  Skipping {name} (not installed)")
            continue
        
        # Construir args completos
        args = config.get('args', [])
        full_args = ["run", "--directory", str(server_dir)] + args
        
        # Add PYTHONPATH to ensure module imports work
        env = config.get('env', {"PYTHONIOENCODING": "utf-8"})
        env["PYTHONPATH"] = "."
        
        mcp_config['mcpServers'][name] = {
            "command": config.get('command', 'uv'),
            "args": full_args,
            "env": env
        }
        
        print(f"✅ Configured: {name}")
    
    # Guardar config
    ANTIGRAVITY_CONFIG.write_text(json.dumps(mcp_config, indent=2))
    print(f"\n✅ Antigravity configured: {ANTIGRAVITY_CONFIG}")
    print("\n⚠️  Restart Antigravity to apply changes")


def list_servers():
    """Listar todos los servidores"""
    registry = load_registry()
    
    print(f"\n{'='*60}")
    print("📋 Registered MCP Servers")
    print(f"{'='*60}\n")
    
    if not registry['servers']:
        print("No servers registered.")
        print(f"Add servers to: {REGISTRY_PATH}")
        return
    
    for name, config in registry['servers'].items():
        server_dir = SERVERS_DIR / config['directory']
        installed = "✅" if server_dir.exists() else "❌"
        enabled = "🟢" if config.get('enabled', True) else "🔴"
        
        print(f"{enabled} {installed} {name}")
        print(f"   {config.get('description', 'No description')}")
        print(f"   Repo: {config.get('repository', 'N/A')}")
        print(f"   Path: {server_dir}")
        print()


def install_all():
    """Instalar todos los servidores"""
    registry = load_registry()
    
    print(f"\n{'='*60}")
    print("🚀 Installing All MCP Servers")
    print(f"{'='*60}")
    
    for name, config in registry['servers'].items():
        if config.get('enabled', True):
            install_server(name, config)
    
    configure_antigravity()


def update_all():
    """Actualizar todos los servidores"""
    registry = load_registry()
    
    print(f"\n{'='*60}")
    print("🔄 Updating All MCP Servers")
    print(f"{'='*60}")
    
    for name, config in registry['servers'].items():
        if config.get('enabled', True):
            update_server(name, config)
    
    configure_antigravity()


def show_config(name):
    """Mostrar configuración de un servidor MCP"""
    registry = load_registry()
    
    if name not in registry['servers']:
        print(f"❌ Server not found: {name}")
        return
    
    config = registry['servers'][name]
    server_dir = SERVERS_DIR / config['directory']
    
    if not server_dir.exists():
        print(f"❌ Server not installed: {name}")
        print(f"   Run: python mcp-manager.py install {name}")
        return
   
    print(f"\n{'='*60}")
    print(f"⚙️  Configuration: {name}")
    print(f"{'='*60}\n")
    
    env_file = server_dir / '.env'
    env_example = server_dir / config.get('env_template', '.env.example')
    
    # Leer configuración actual
    current_config = {}
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    current_config[key.strip()] = value.strip()
    
    # Mostrar cada variable requerida
    env_required = config.get('env_required', [])
    
    if env_required:
        print("**Required Environment Variables:**\n")
        for var in env_required:
            value = current_config.get(var, '')
            if value:
                # Mask sensitive values
                if 'TOKEN' in var or 'PASSWORD' in var or 'SECRET' in var:
                    masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
                    print(f"  ✅ {var}: {masked}")
                else:
                    print(f"  ✅ {var}: {value}")
            else:
                print(f"  ❌ {var}: Not configured")
        print()
    
    # Mostrar otras variables
    other_vars = [k for k in current_config.keys() if k not in env_required]
    if other_vars:
        print("**Optional Variables:**\n")
        for var in other_vars:
            value = current_config[var]
            print(f"  ℹ️  {var}: {value}")
        print()
    
    # Info de archivos
    print("**Configuration Files:**")
    print(f"  Config: {env_file}")
    if env_example.exists():
        print(f"  Template: {env_example}")
    print()
    
    # Acciones disponibles
    print("**Actions:**")
    print(f"  Configure: python mcp-manager.py configure {name}")
    print(f"  Edit manually: {env_file}")


def configure_server(name):
    """Configurar un servidor MCP interactivamente"""
    registry = load_registry()
    
    if name not in registry['servers']:
        print(f"❌ Server not found: {name}")
        return
    
    config = registry['servers'][name]
    server_dir = SERVERS_DIR / config['directory']
    
    if not server_dir.exists():
        print(f"❌ Server not installed: {name}")
        print(f"   Run: python mcp-manager.py install {name}")
        return
    
    print(f"\n{'='*60}")
    print(f"⚙️  Configuring: {name}")
    print(f"   {config.get('description', 'No description')}")
    print(f"{'='*60}\n")
    
    env_file = server_dir / '.env'
    env_example = server_dir / config.get('env_template', '.env.example')
    
    # Leer configuración actual
    current_config = {}
    if env_file.exists():
        print(f"📄 Found existing configuration\n")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    current_config[key.strip()] = value.strip()
    else:
        print(f"📝 Creating new configuration\n")
    
    # Configurar variables requeridas
    env_required = config.get('env_required', [])
    new_config = {}
    
    if env_required:
        print("Please provide the following required variables:\n")
        
        for var in env_required:
            current_value = current_config.get(var, '')
            
            if current_value:
                # Mask sensitive values in prompt
                if 'TOKEN' in var or 'PASSWORD' in var or 'SECRET' in var:
                    display_value = f"{current_value[:4]}...{current_value[-4:]}" if len(current_value) > 8 else "***"
                else:
                    display_value = current_value
                
                print(f"{var}")
                print(f"  Current: {display_value}")
            else:
                print(f"{var}")
                print(f"  Current: (not set)")
            
            value = input(f"  Enter value (or press Enter to keep current): ").strip()
            
            if value:
                new_config[var] = value
            elif current_value:
                new_config[var] = current_value
            else:
                print(f"  ⚠️  Skipping {var} (not set)")
            
            print()
    
    # Mantener otras variables existentes
    for key, value in current_config.items():
        if key not in new_config:
            new_config[key] = value
    
    # Guardar configuración
    print("="*60)
    print("Saving configuration...")
    print("="*60)
    
    env_content = f"# {name} - MCP Server Configuration\n"
    env_content += "# Managed by Protonion MCP Manager\n\n"
    
    # Primero las requeridas
    for var in env_required:
        if var in new_config:
            env_content += f"{var}={new_config[var]}\n"
    
    # Luego las opcionales
    other_vars = [k for k in new_config.keys() if k not in env_required]
    if other_vars:
        env_content += "\n# Optional variables\n"
        for var in other_vars:
            env_content += f"{var}={new_config[var]}\n"
    
    env_file.write_text(env_content)
    print(f"✅ Configuration saved to: {env_file}\n")
    
    # Verificar si hay script de configuración personalizado
    custom_script = server_dir / "configure.py"
    if custom_script.exists():
        print("💡 Tip: This server has a custom configuration wizard:")
        print(f"   Run: python {custom_script}")
        print()


def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║         Protonion MCP Manager v1.0                    ║
    ║     Gestiona todos tus servidores MCP                 ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  mcp-manager.py list                  - List all servers")
        print("  mcp-manager.py install [name]        - Install server(s)")
        print("  mcp-manager.py install-all           - Install all servers")
        print("  mcp-manager.py update [name]         - Update server(s)")
        print("  mcp-manager.py update-all            - Update all servers")
        print("  mcp-manager.py show-config [name]    - Show server configuration")
        print("  mcp-manager.py configure [name]      - Configure server (interactive)")
        print("  mcp-manager.py config                - Configure Antigravity")
        print()
        print(f"Registry: {REGISTRY_PATH}")
        print(f"Servers:  {SERVERS_DIR}")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_servers()
    
    elif command == "install-all":
        install_all()
    
    elif command == "install":
        if len(sys.argv) < 3:
            print("❌ Specify server name")
            return
        
        name = sys.argv[2]
        registry = load_registry()
        
        if name not in registry['servers']:
            print(f"❌ Server not found: {name}")
            return
        
        install_server(name, registry['servers'][name])
        configure_antigravity()
    
    elif command == "update-all":
        update_all()
    
    elif command == "update":
        if len(sys.argv) < 3:
            print("❌ Specify server name")
            return
        
        name = sys.argv[2]
        registry = load_registry()
        
        if name not in registry['servers']:
            print(f"❌ Server not found: {name}")
            return
        
        update_server(name, registry['servers'][name])
        configure_antigravity()
    
    elif command == "show-config":
        if len(sys.argv) < 3:
            print("❌ Specify server name")
            return
        
        show_config(sys.argv[2])
    
    elif command == "configure":
        if len(sys.argv) < 3:
            print("❌ Specify server name")
            return
        
        configure_server(sys.argv[2])
    
    elif command == "config":
        configure_antigravity()
    
    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()
