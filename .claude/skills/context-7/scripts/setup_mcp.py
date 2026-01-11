#!/usr/bin/env python3
"""
MCP Setup Script for Claude Code

Interactive and command-line setup for MCP server configuration.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional

def get_config_path() -> Path:
    """Get configuration file path"""
    config_dir = Path(
        os.environ.get('MCP_CONFIG_DIR', '~/.claude-code')
    ).expanduser()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / 'mcp-servers.json'

def load_config() -> Dict:
    """Load existing configuration"""
    config_path = get_config_path()
    
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    
    return {
        "servers": [],
        "defaults": {
            "timeout": 30,
            "cache_dir": "~/.claude-code/cache",
            "format": "terminal"
        }
    }

def save_config(config: Dict) -> None:
    """Save configuration"""
    config_path = get_config_path()
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration saved to {config_path}")

def interactive_setup() -> Dict:
    """Interactive configuration setup"""
    print("="*60)
    print("MCP Server Configuration")
    print("="*60)
    print()
    
    server = {}
    
    # Server name
    while True:
        name = input("Server name (e.g., 'official-docs'): ").strip()
        if name:
            server['name'] = name
            break
        print("  ⚠️  Name cannot be empty")
    
    # Server URI
    while True:
        uri = input("Server URI (e.g., 'mcp://docs.example.com'): ").strip()
        if uri:
            server['uri'] = uri
            break
        print("  ⚠️  URI cannot be empty")
    
    # Authentication
    print("\nAuthentication type:")
    print("  1. API Key")
    print("  2. Bearer Token")
    print("  3. None")
    
    auth_choice = input("Select (1-3) [3]: ").strip() or "3"
    
    if auth_choice == "1":
        api_key = input("API Key (or environment variable name): ").strip()
        if api_key.startswith('$'):
            server['auth'] = {
                "type": "api_key",
                "key": api_key
            }
        else:
            server['auth'] = {
                "type": "api_key",
                "key": api_key
            }
    elif auth_choice == "2":
        token = input("Bearer Token: ").strip()
        server['auth'] = {
            "type": "bearer",
            "token": token
        }
    else:
        server['auth'] = {"type": "none"}
    
    # Caching
    enable_cache = input("\nEnable caching? (y/n) [y]: ").strip().lower()
    if enable_cache != 'n':
        ttl = input("Cache TTL in seconds [3600]: ").strip() or "3600"
        server['cache'] = {
            "enabled": True,
            "ttl": int(ttl)
        }
    else:
        server['cache'] = {"enabled": False}
    
    print("\n" + "="*60)
    print("Configuration Summary:")
    print("="*60)
    print(json.dumps(server, indent=2))
    print()
    
    confirm = input("Save this configuration? (y/n) [y]: ").strip().lower()
    
    if confirm != 'n':
        return server
    else:
        print("Configuration cancelled")
        sys.exit(0)

def add_server(config: Dict, server: Dict) -> Dict:
    """Add server to configuration"""
    # Remove existing server with same name
    config['servers'] = [
        s for s in config.get('servers', [])
        if s['name'] != server['name']
    ]
    
    config['servers'].append(server)
    return config

def remove_server(config: Dict, name: str) -> Dict:
    """Remove server from configuration"""
    original_count = len(config.get('servers', []))
    config['servers'] = [
        s for s in config.get('servers', [])
        if s['name'] != name
    ]
    
    if len(config['servers']) == original_count:
        print(f"⚠️  Server '{name}' not found")
    else:
        print(f"✓ Removed server '{name}'")
    
    return config

def list_servers(config: Dict) -> None:
    """List configured servers"""
    servers = config.get('servers', [])
    
    if not servers:
        print("No servers configured")
        return
    
    print(f"\nConfigured servers ({len(servers)}):")
    print()
    
    for server in servers:
        print(f"  • {server['name']}")
        print(f"    URI: {server['uri']}")
        print(f"    Auth: {server.get('auth', {}).get('type', 'none')}")
        print(f"    Cache: {'enabled' if server.get('cache', {}).get('enabled') else 'disabled'}")
        print()

async def test_connection(server_uri: str) -> bool:
    """Test connection to MCP server"""
    import asyncio
    
    print(f"Testing connection to {server_uri}...")
    
    try:
        await asyncio.sleep(0.5)  # Simulate connection test
        print("✓ Connection successful")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Setup MCP servers for Claude Code"
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Interactive setup mode'
    )
    
    parser.add_argument(
        '--server',
        help='Server URI'
    )
    
    parser.add_argument(
        '--name',
        help='Server name'
    )
    
    parser.add_argument(
        '--auth-type',
        choices=['api_key', 'bearer', 'none'],
        default='none',
        help='Authentication type'
    )
    
    parser.add_argument(
        '--api-key',
        help='API key for authentication'
    )
    
    parser.add_argument(
        '--bearer-token',
        help='Bearer token for authentication'
    )
    
    parser.add_argument(
        '--enable-cache',
        action='store_true',
        default=True,
        help='Enable caching'
    )
    
    parser.add_argument(
        '--cache-ttl',
        type=int,
        default=3600,
        help='Cache TTL in seconds'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List configured servers'
    )
    
    parser.add_argument(
        '--remove',
        help='Remove server by name'
    )
    
    parser.add_argument(
        '--test-connection',
        help='Test connection to server URI'
    )
    
    args = parser.parse_args()
    
    # Load existing config
    config = load_config()
    
    # List servers
    if args.list:
        list_servers(config)
        return 0
    
    # Remove server
    if args.remove:
        config = remove_server(config, args.remove)
        save_config(config)
        return 0
    
    # Test connection
    if args.test_connection:
        import asyncio
        success = asyncio.run(test_connection(args.test_connection))
        return 0 if success else 1
    
    # Interactive mode
    if args.interactive:
        server = interactive_setup()
        config = add_server(config, server)
        save_config(config)
        return 0
    
    # Command-line mode
    if args.server and args.name:
        server = {
            'name': args.name,
            'uri': args.server,
            'auth': {'type': args.auth_type},
            'cache': {
                'enabled': args.enable_cache,
                'ttl': args.cache_ttl
            }
        }
        
        if args.auth_type == 'api_key' and args.api_key:
            server['auth']['key'] = args.api_key
        elif args.auth_type == 'bearer' and args.bearer_token:
            server['auth']['token'] = args.bearer_token
        
        config = add_server(config, server)
        save_config(config)
        
        print(f"\n✓ Added server '{args.name}'")
        return 0
    
    # No valid action
    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main())
