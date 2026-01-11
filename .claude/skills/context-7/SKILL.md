---
name: claude-code-mcp
description: MCP integration for Claude Code command-line tool. Use when working in terminal environments, CLI coding workflows, or when users need to connect Claude Code to MCP servers for accessing documentation, code examples, project context, or development tools directly from the command line.
---

# Claude Code MCP Integration

This skill enables Claude Code to connect with MCP servers for enhanced command-line development workflows.

## Overview

Claude Code is a command-line tool for agentic coding. This skill provides:

1. MCP server connection from terminal
2. Documentation access during coding sessions
3. Code example retrieval and insertion
4. Project context integration
5. Development tool orchestration

## Quick Start

### Connect to MCP Server

```bash
# Discover server capabilities
python mcp_client.py discover mcp://localhost:3000

# Fetch documentation
python mcp_client.py fetch docs://api/reference

# Search for code examples
python mcp_client.py search "authentication implementation"
```

## Core Workflows

### Workflow 1: Setup MCP Connection

**When to use**: First time connecting or configuring a new MCP server

**Steps**:
1. Create configuration file using `scripts/setup_mcp.py`
2. Test connection with discovery command
3. Verify available resources and tools
4. Save configuration for reuse

**Example**:
```bash
# Interactive setup
python scripts/setup_mcp.py --interactive

# Or configure directly
python scripts/setup_mcp.py \
  --server mcp://docs.example.com \
  --name "official-docs" \
  --auth-type api_key \
  --api-key $API_KEY
```

### Workflow 2: Fetch Documentation During Coding

**When to use**: Need API reference, examples, or documentation while coding

**Steps**:
1. Identify needed documentation (API, library, pattern)
2. Query MCP server using `mcp_client.py`
3. Format output for terminal or integrate into code
4. Cache for offline access if needed

**Example**:
```bash
# Fetch and display in terminal
python mcp_client.py fetch docs://api/authentication --format terminal

# Save to file
python mcp_client.py fetch docs://api/authentication --output docs/auth.md

# Insert code example into file
python mcp_client.py insert code://examples/jwt-auth --file src/auth.py --line 45
```

### Workflow 3: Search Across Multiple Servers

**When to use**: Research implementation patterns, compare approaches, or find best practices

**Steps**:
1. Query all configured MCP servers
2. Aggregate and rank results
3. Display formatted results in terminal
4. Select and retrieve specific resources

**Example**:
```bash
# Search all servers
python mcp_client.py search "error handling best practices" --all-servers

# Search specific server
python mcp_client.py search "react hooks" --server official-docs

# Interactive mode
python mcp_client.py search --interactive
```

### Workflow 4: Project Context Integration

**When to use**: Initialize project with MCP resources or sync project documentation

**Steps**:
1. Scan project for documentation needs
2. Map to MCP resources
3. Fetch and organize in project structure
4. Set up auto-sync if needed

**Example**:
```bash
# Initialize project docs
python scripts/init_project_docs.py --project-dir . --server official-docs

# Update project docs
python scripts/sync_docs.py --watch
```

## CLI Tool Reference

### mcp_client.py Commands

**discover**: List server capabilities
```bash
python mcp_client.py discover <server_uri> [--output FILE]
```

**fetch**: Retrieve specific resource
```bash
python mcp_client.py fetch <resource_uri> [--format terminal|markdown|json] [--output FILE]
```

**search**: Search across servers
```bash
python mcp_client.py search <query> [--server NAME] [--all-servers] [--limit N]
```

**insert**: Insert code into file
```bash
python mcp_client.py insert <resource_uri> --file PATH --line NUMBER [--language LANG]
```

**list**: Show configured servers
```bash
python mcp_client.py list [--verbose]
```

## Terminal Output Formatting

Claude Code should format MCP responses for optimal terminal display:

### Code Examples
- Use syntax highlighting (via pygments)
- Show language identifier
- Include line numbers for reference
- Add context comments

### Documentation
- Use terminal width (80 cols default)
- Format headers with ASCII art or emoji
- Highlight important sections
- Include navigation hints

### API References
- Tabular format for parameters
- Color-code required vs optional
- Show examples inline
- Link to full documentation

See `references/terminal-formatting.md` for detailed formatting guidelines.

## Configuration Management

MCP servers are configured in `~/.claude-code/mcp-servers.json`:

```json
{
  "servers": [
    {
      "name": "official-docs",
      "uri": "mcp://docs.example.com",
      "auth": {
        "type": "api_key",
        "key": "${MCP_API_KEY}"
      },
      "cache": {
        "enabled": true,
        "ttl": 3600
      }
    }
  ],
  "defaults": {
    "timeout": 30,
    "cache_dir": "~/.claude-code/cache",
    "format": "terminal"
  }
}
```

## Integration Patterns

### Pattern 1: Inline Documentation

Fetch and display docs without leaving terminal:

```bash
# In coding session
$ python mcp_client.py fetch docs://api/users --format terminal | less

# Quick reference
$ python mcp_client.py fetch docs://api/users --section "POST /users" --brief
```

### Pattern 2: Code Generation Pipeline

Use MCP examples as templates:

```bash
# Fetch template
$ python mcp_client.py fetch code://templates/crud-api --output template.py

# Customize with sed/awk
$ sed 's/{{MODEL}}/User/g' template.py > src/user_api.py
```

### Pattern 3: Documentation-Driven Development

Keep docs in sync with code:

```bash
# Watch for changes
$ python scripts/sync_docs.py --watch --project . --server official-docs

# Validate implementation against docs
$ python scripts/validate_api.py --spec docs://api/spec --implementation src/
```

## Advanced Features

For advanced usage scenarios:

- **Custom parsers**: See `references/custom-parsers.md`
- **Caching strategies**: See `references/caching.md`
- **Multi-server setup**: See `references/multi-server.md`
- **CI/CD integration**: See `references/ci-integration.md`

## Error Handling

Common issues and solutions:

1. **Connection refused**: Check server URI and network
   ```bash
   python mcp_client.py test-connection mcp://server
   ```

2. **Authentication failed**: Verify API key
   ```bash
   python scripts/setup_mcp.py --test-auth
   ```

3. **Resource not found**: List available resources
   ```bash
   python mcp_client.py discover mcp://server --resources-only
   ```

4. **Rate limit exceeded**: Check cache or reduce requests
   ```bash
   python mcp_client.py stats --server official-docs
   ```

## Best Practices for Claude Code

1. **Cache aggressively** - Terminal sessions need fast response
2. **Format for readability** - Use colors, spacing, and structure
3. **Provide context** - Show where docs came from, when cached
4. **Support offline mode** - Cache critical documentation
5. **Keep configs simple** - Easy to version control and share
6. **Log for debugging** - Store in `~/.claude-code/logs/`
7. **Integrate with editor** - Support vim/emacs/vscode plugins

## Environment Variables

```bash
# MCP configuration
export MCP_CONFIG_DIR="$HOME/.claude-code"
export MCP_CACHE_DIR="$HOME/.claude-code/cache"
export MCP_API_KEY="your-api-key"

# Output preferences
export MCP_OUTPUT_FORMAT="terminal"  # terminal, markdown, json
export MCP_COLOR="auto"              # always, auto, never
export MCP_PAGER="less -R"           # Pager for long output
```

## Shell Integration

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# MCP quick commands
alias mcp-docs='python mcp_client.py fetch'
alias mcp-search='python mcp_client.py search'
alias mcp-list='python mcp_client.py list'

# Function for quick doc lookup
mcp() {
  if [ "$1" = "help" ]; then
    python mcp_client.py fetch "docs://api/$2" --format terminal | less -R
  else
    python mcp_client.py "$@"
  fi
}
```

## Examples

### Example 1: Research Authentication Pattern
```bash
# Search multiple servers
$ python mcp_client.py search "JWT authentication" --all-servers

# View best result
$ python mcp_client.py fetch docs://api/auth/jwt --format terminal

# Get code example
$ python mcp_client.py fetch code://examples/jwt-auth --language python
```

### Example 2: Quick API Reference
```bash
# Interactive search
$ python mcp_client.py search --interactive
> Query: user management
> Select: [2] User CRUD Operations
> [Displays formatted documentation]
```

### Example 3: Project Setup
```bash
# Initialize new project with docs
$ python scripts/init_project_docs.py \
    --project-dir ./my-api \
    --server official-docs \
    --topics "authentication,users,errors"

# This creates:
# ./my-api/docs/authentication.md
# ./my-api/docs/users.md
# ./my-api/docs/errors.md
```
