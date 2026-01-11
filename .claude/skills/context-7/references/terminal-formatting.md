# Terminal Formatting Guidelines

Best practices for formatting MCP content for terminal display in Claude Code.

## Core Principles

1. **Readability First** - Use spacing and colors to enhance clarity
2. **Consistent Width** - Default to 80 columns for compatibility
3. **Progressive Disclosure** - Show summaries first, details on demand
4. **Color Coding** - Use colors semantically, not decoratively

## ANSI Color Codes

```python
COLORS = {
    'header': '\033[95m',     # Magenta
    'blue': '\033[94m',       # Blue
    'cyan': '\033[96m',       # Cyan
    'green': '\033[92m',      # Green
    'yellow': '\033[93m',     # Yellow
    'red': '\033[91m',        # Red
    'bold': '\033[1m',        # Bold
    'underline': '\033[4m',   # Underline
    'end': '\033[0m'          # Reset
}
```

## Color Usage Guidelines

### Headers and Titles
- **H1 (# )**: Bold + Blue
- **H2 (## )**: Bold + Cyan  
- **H3 (### )**: Bold + Green
- **H4+**: Regular + Yellow

```python
def format_header(level, text):
    colors = {
        1: BOLD + BLUE,
        2: BOLD + CYAN,
        3: BOLD + GREEN,
        4: YELLOW
    }
    return f"{colors.get(level, '')}{text}{END}"
```

### Content Elements
- **Code blocks**: Yellow border, white text
- **Inline code**: Cyan background
- **Links/URIs**: Cyan + underline
- **Success messages**: Green
- **Warnings**: Yellow
- **Errors**: Red + bold
- **Metadata**: Gray (dim)

## Code Block Formatting

### With Syntax Highlighting

```python
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter

def format_code_block(code, language='python'):
    lexer = get_lexer_by_name(language, stripall=True)
    formatter = TerminalFormatter()
    return highlight(code, lexer, formatter)
```

### Without Syntax Highlighting

```
┌────────────────────────────────────────┐
│ Python                                  │
├────────────────────────────────────────┤
│ def hello():                           │
│     print("Hello, World!")             │
└────────────────────────────────────────┘
```

## API Reference Formatting

### Endpoint Display

```
╔══════════════════════════════════════════════════════════════╗
║ POST /api/users                                              ║
╠══════════════════════════════════════════════════════════════╣
║ Create a new user account                                    ║
╚══════════════════════════════════════════════════════════════╝

Parameters:
┌──────────┬──────────┬──────────┬─────────────────────────┐
│ Name     │ Location │ Required │ Description             │
├──────────┼──────────┼──────────┼─────────────────────────┤
│ email    │ body     │ Yes      │ User email address      │
│ password │ body     │ Yes      │ User password (min 8)   │
│ name     │ body     │ No       │ User display name       │
└──────────┴──────────┴──────────┴─────────────────────────┘

Response: 201 Created
{
  "id": "123",
  "email": "user@example.com",
  "created_at": "2025-01-11T10:30:00Z"
}
```

### Implementation

```python
def format_api_endpoint(endpoint):
    output = []
    
    # Header
    output.append("╔" + "═"*60 + "╗")
    output.append(f"║ {endpoint['method']} {endpoint['path']:<54} ║")
    output.append("╠" + "═"*60 + "╣")
    output.append(f"║ {endpoint['description']:<58} ║")
    output.append("╚" + "═"*60 + "╝")
    
    # Parameters table
    if endpoint.get('parameters'):
        output.append("\nParameters:")
        output.append(format_table(endpoint['parameters']))
    
    # Response example
    if endpoint.get('response'):
        output.append(f"\nResponse: {endpoint['status']}")
        output.append(format_json(endpoint['response']))
    
    return '\n'.join(output)
```

## Table Formatting

### ASCII Table

```python
def format_table(headers, rows):
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    
    # Top border
    output = ["┌" + "┬".join("─" * (w+2) for w in widths) + "┐"]
    
    # Headers
    header_row = "│" + "│".join(f" {h:<{widths[i]}} " 
                                 for i, h in enumerate(headers)) + "│"
    output.append(header_row)
    
    # Separator
    output.append("├" + "┼".join("─" * (w+2) for w in widths) + "┤")
    
    # Data rows
    for row in rows:
        data_row = "│" + "│".join(f" {str(cell):<{widths[i]}} " 
                                   for i, cell in enumerate(row)) + "│"
        output.append(data_row)
    
    # Bottom border
    output.append("└" + "┴".join("─" * (w+2) for w in widths) + "┘")
    
    return '\n'.join(output)
```

## Search Results Formatting

```
🔎 Search Results (3):

[1] Authentication API Documentation                      ★★★★★ 95%
    docs://api/authentication
    Server: official-docs
    JWT-based authentication system for API access...
    
[2] JWT Implementation Examples                           ★★★★☆ 87%
    code://examples/jwt
    Server: official-docs
    Working code examples for JWT authentication...

[3] User Authentication Best Practices                    ★★★☆☆ 76%
    docs://guides/auth-security
    Server: community-wiki
    Security considerations for user authentication...
```

### Implementation

```python
def format_search_results(results):
    output = [f"\n🔎 Search Results ({len(results)}):\n"]
    
    for i, result in enumerate(results, 1):
        relevance = result['relevance'] * 100
        stars = "★" * int(relevance / 20) + "☆" * (5 - int(relevance / 20))
        
        output.append(
            f"[{BOLD}{i}{END}] {BOLD}{result['title']}{END}"
            f"{' ' * (50 - len(result['title']))}{stars} {relevance:.0f}%"
        )
        output.append(f"    {CYAN}{result['uri']}{END}")
        output.append(f"    Server: {result['server']}")
        output.append(f"    {result['snippet']}")
        output.append("")
    
    return '\n'.join(output)
```

## Progress Indicators

### Spinner

```python
import itertools
import sys
import time

def show_spinner(message):
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    
    for _ in range(30):  # 3 seconds
        sys.stdout.write(f'\r{next(spinner)} {message}')
        sys.stdout.flush()
        time.sleep(0.1)
    
    sys.stdout.write('\r✓ ' + message + '\n')
```

### Progress Bar

```python
def progress_bar(current, total, width=50):
    percentage = current / total
    filled = int(width * percentage)
    bar = '█' * filled + '░' * (width - filled)
    
    print(f'\r[{bar}] {percentage:.0%} ({current}/{total})', end='')
    
    if current == total:
        print()  # New line when complete
```

## Status Messages

### Success

```
✓ Configuration saved to ~/.claude-code/mcp-servers.json
✓ Connected to official-docs
✓ Documentation fetched successfully
```

### Warning

```
⚠️  Cache expired, fetching fresh data...
⚠️  Server response took longer than expected
⚠️  No servers configured
```

### Error

```
✗ Connection failed: timeout after 30s
✗ Authentication failed: invalid API key
✗ Resource not found: docs://api/nonexistent
```

### Info

```
ℹ️  Using cached response (5 minutes old)
ℹ️  3 servers configured
ℹ️  Rate limit: 95/100 requests remaining
```

## Documentation Navigation

### Breadcrumbs

```
Home > API Reference > Authentication > JWT Tokens
```

### Section Markers

```
════════════════════════════════════════════════════════════════
 AUTHENTICATION API
════════════════════════════════════════════════════════════════

──────────────────────────────────────────────────────────────
 Endpoints
──────────────────────────────────────────────────────────────
```

## Paging Long Content

```python
def paginate_content(content, page_height=40):
    """Show content with 'more' prompt"""
    lines = content.split('\n')
    
    for i in range(0, len(lines), page_height):
        page = lines[i:i+page_height]
        print('\n'.join(page))
        
        if i + page_height < len(lines):
            input(f"\n{BOLD}Press Enter for more...{END}")
        else:
            print(f"\n{BOLD}(End of content){END}")
```

## Best Practices

1. **Test in multiple terminals** - iTerm, Terminal.app, Windows Terminal, etc.
2. **Support NO_COLOR environment variable** - Disable colors when set
3. **Respect terminal width** - Use `shutil.get_terminal_size()`
4. **Provide plain text fallback** - For piping to files
5. **Use Unicode carefully** - ASCII fallback for compatibility
6. **Keep it responsive** - Update UI during long operations
7. **Make output greppable** - Important info on single lines

## Environment Variables

```bash
# Color preferences
export MCP_COLOR=auto        # always, auto, never
export NO_COLOR=1            # Disable colors (industry standard)

# Output preferences  
export MCP_PAGER=less        # Pager for long output
export MCP_WIDTH=100         # Override terminal width
```

## Testing Output

```python
def test_formatting():
    """Test all formatting functions"""
    
    # Test colors
    print(colored("Header", BOLD + BLUE))
    print(colored("Success", GREEN))
    print(colored("Warning", YELLOW))
    print(colored("Error", RED))
    
    # Test table
    headers = ["Name", "Type", "Required"]
    rows = [
        ["email", "string", "Yes"],
        ["password", "string", "Yes"]
    ]
    print(format_table(headers, rows))
    
    # Test progress
    for i in range(101):
        progress_bar(i, 100)
        time.sleep(0.01)
```
