#!/usr/bin/env python3
"""
MCP Client for Claude Code

Command-line interface for interacting with MCP servers from terminal.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Terminal colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def colored(text: str, color: str) -> str:
    """Add color to text for terminal output"""
    if os.environ.get('MCP_COLOR', 'auto') == 'never':
        return text
    return f"{color}{text}{Colors.END}"

class MCPClient:
    """MCP client for terminal usage"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.expanduser(
            os.environ.get('MCP_CONFIG_DIR', '~/.claude-code/mcp-servers.json')
        )
        self.config = self._load_config()
        self.cache_dir = Path(
            os.environ.get('MCP_CACHE_DIR', '~/.claude-code/cache')
        ).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict:
        """Load MCP server configuration"""
        config_path = Path(self.config_path).expanduser()
        
        if not config_path.exists():
            return {
                "servers": [],
                "defaults": {
                    "timeout": 30,
                    "cache_dir": "~/.claude-code/cache",
                    "format": "terminal"
                }
            }
        
        with open(config_path) as f:
            return json.load(f)
    
    def get_server(self, name: str) -> Optional[Dict]:
        """Get server configuration by name"""
        for server in self.config.get('servers', []):
            if server['name'] == name:
                return server
        return None
    
    async def discover(self, server_uri: str) -> Dict:
        """Discover server capabilities"""
        print(colored(f"🔍 Discovering: {server_uri}", Colors.BLUE))
        await asyncio.sleep(0.5)  # Simulate connection
        
        # Simulated discovery
        discovery = {
            "server": server_uri,
            "resources": [
                {
                    "uri": "docs://api/authentication",
                    "name": "Authentication API",
                    "type": "documentation"
                },
                {
                    "uri": "code://examples/jwt",
                    "name": "JWT Examples",
                    "type": "code"
                }
            ],
            "tools": [
                {
                    "name": "search_docs",
                    "description": "Search documentation"
                }
            ]
        }
        
        return discovery
    
    async def fetch(self, resource_uri: str, format_type: str = "terminal") -> str:
        """Fetch resource from MCP server"""
        print(colored(f"📥 Fetching: {resource_uri}", Colors.CYAN))
        await asyncio.sleep(0.3)
        
        # Simulated content
        content = f"""# Authentication API

## Overview
Provides JWT-based authentication for API access.

## Endpoints

### POST /auth/login
Authenticate user and receive JWT token.

**Request:**
```json
{{
  "email": "user@example.com",
  "password": "password123"
}}
```

**Response:**
```json
{{
  "token": "eyJhbGc...",
  "expires_in": 3600
}}
```

### Example Code (Python):
```python
import requests

def login(email, password):
    response = requests.post(
        'https://api.example.com/auth/login',
        json={{'email': email, 'password': password}}
    )
    return response.json()['token']
```
"""
        
        if format_type == "terminal":
            return self._format_for_terminal(content)
        elif format_type == "json":
            return json.dumps({"content": content, "uri": resource_uri}, indent=2)
        else:
            return content
    
    def _format_for_terminal(self, content: str) -> str:
        """Format content for terminal display"""
        lines = content.split('\n')
        formatted = []
        
        for line in lines:
            if line.startswith('# '):
                formatted.append(colored(line, Colors.BOLD + Colors.BLUE))
            elif line.startswith('## '):
                formatted.append(colored(line, Colors.BOLD + Colors.CYAN))
            elif line.startswith('### '):
                formatted.append(colored(line, Colors.BOLD + Colors.GREEN))
            elif line.startswith('```'):
                formatted.append(colored(line, Colors.YELLOW))
            else:
                formatted.append(line)
        
        return '\n'.join(formatted)
    
    async def search(self, query: str, server_name: Optional[str] = None, 
                    all_servers: bool = False) -> List[Dict]:
        """Search for documentation"""
        print(colored(f"🔎 Searching for: '{query}'", Colors.BLUE))
        
        servers = []
        if all_servers:
            servers = self.config.get('servers', [])
        elif server_name:
            server = self.get_server(server_name)
            if server:
                servers = [server]
        else:
            # Use first server as default
            servers = self.config.get('servers', [])[:1]
        
        await asyncio.sleep(0.5)
        
        # Simulated results
        results = [
            {
                "title": "Authentication API Documentation",
                "uri": "docs://api/authentication",
                "relevance": 0.95,
                "server": servers[0]['name'] if servers else "unknown",
                "snippet": "JWT-based authentication system for API access..."
            },
            {
                "title": "JWT Implementation Examples",
                "uri": "code://examples/jwt",
                "relevance": 0.87,
                "server": servers[0]['name'] if servers else "unknown",
                "snippet": "Working code examples for JWT authentication..."
            }
        ]
        
        return results
    
    def list_servers(self, verbose: bool = False) -> None:
        """List configured MCP servers"""
        servers = self.config.get('servers', [])
        
        if not servers:
            print(colored("⚠️  No MCP servers configured", Colors.YELLOW))
            print(f"\nRun: python scripts/setup_mcp.py --interactive")
            return
        
        print(colored(f"\n📡 Configured MCP Servers ({len(servers)}):", Colors.BOLD))
        print()
        
        for server in servers:
            name = colored(server['name'], Colors.BOLD + Colors.GREEN)
            uri = server['uri']
            print(f"  • {name}")
            print(f"    URI: {uri}")
            
            if verbose:
                auth = server.get('auth', {})
                print(f"    Auth: {auth.get('type', 'none')}")
                cache = server.get('cache', {})
                print(f"    Cache: {'enabled' if cache.get('enabled') else 'disabled'}")
            print()

async def cmd_discover(args):
    """Discover command"""
    client = MCPClient()
    discovery = await client.discover(args.server_uri)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(discovery, f, indent=2)
        print(colored(f"\n✓ Saved to {args.output}", Colors.GREEN))
    else:
        print(colored("\n=== Server Discovery ===", Colors.BOLD))
        print(f"\nResources ({len(discovery['resources'])}):")
        for r in discovery['resources']:
            print(f"  • {r['name']}")
            print(f"    {colored(r['uri'], Colors.CYAN)}")
        
        print(f"\nTools ({len(discovery['tools'])}):")
        for t in discovery['tools']:
            print(f"  • {t['name']}: {t['description']}")

async def cmd_fetch(args):
    """Fetch command"""
    client = MCPClient()
    content = await client.fetch(args.resource_uri, args.format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(content)
        print(colored(f"\n✓ Saved to {args.output}", Colors.GREEN))
    else:
        print("\n" + "="*80)
        print(content)
        print("="*80)

async def cmd_search(args):
    """Search command"""
    client = MCPClient()
    results = await client.search(
        args.query,
        server_name=args.server,
        all_servers=args.all_servers
    )
    
    print(colored(f"\n📚 Search Results ({len(results)}):", Colors.BOLD))
    print()
    
    for i, result in enumerate(results, 1):
        relevance = result['relevance'] * 100
        print(f"{colored(f'[{i}]', Colors.BOLD)} {result['title']}")
        print(f"    Relevance: {relevance:.0f}%")
        print(f"    URI: {colored(result['uri'], Colors.CYAN)}")
        print(f"    Server: {result['server']}")
        print(f"    {result['snippet']}")
        print()
    
    if args.limit and len(results) > args.limit:
        print(colored(f"Showing top {args.limit} results", Colors.YELLOW))

def cmd_list(args):
    """List command"""
    client = MCPClient()
    client.list_servers(verbose=args.verbose)

def main():
    parser = argparse.ArgumentParser(
        description="MCP Client for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Discover server capabilities')
    discover_parser.add_argument('server_uri', help='MCP server URI')
    discover_parser.add_argument('--output', help='Output file (JSON)')
    
    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch resource')
    fetch_parser.add_argument('resource_uri', help='Resource URI')
    fetch_parser.add_argument('--format', choices=['terminal', 'markdown', 'json'],
                             default='terminal', help='Output format')
    fetch_parser.add_argument('--output', help='Output file')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search documentation')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--server', help='Server name')
    search_parser.add_argument('--all-servers', action='store_true',
                              help='Search all configured servers')
    search_parser.add_argument('--limit', type=int, help='Limit results')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List configured servers')
    list_parser.add_argument('--verbose', '-v', action='store_true',
                            help='Show detailed information')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == 'discover':
        asyncio.run(cmd_discover(args))
    elif args.command == 'fetch':
        asyncio.run(cmd_fetch(args))
    elif args.command == 'search':
        asyncio.run(cmd_search(args))
    elif args.command == 'list':
        cmd_list(args)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(colored("\n\n⚠️  Interrupted", Colors.YELLOW))
        sys.exit(130)
    except Exception as e:
        print(colored(f"\n❌ Error: {e}", Colors.RED), file=sys.stderr)
        sys.exit(1)
