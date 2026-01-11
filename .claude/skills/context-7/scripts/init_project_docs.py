#!/usr/bin/env python3
"""
Initialize Project Documentation from MCP Server

Fetch and organize documentation for a project from MCP servers.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional

class ProjectDocsInitializer:
    """Initialize project documentation from MCP"""
    
    def __init__(self, project_dir: Path, server_name: str):
        self.project_dir = project_dir
        self.server_name = server_name
        self.docs_dir = project_dir / 'docs'
        self.docs_dir.mkdir(parents=True, exist_ok=True)
    
    async def fetch_topic_docs(self, topic: str) -> str:
        """Fetch documentation for a specific topic"""
        print(f"📥 Fetching: {topic}")
        await asyncio.sleep(0.3)
        
        # Simulated documentation content
        docs = {
            "authentication": """# Authentication

## Overview
JWT-based authentication system for API access.

## Setup
1. Configure authentication provider
2. Generate JWT secret key
3. Set token expiration time

## Usage
```python
from auth import authenticate

token = authenticate(username, password)
```

## Best Practices
- Use strong secret keys
- Rotate keys regularly
- Implement refresh tokens
- Set appropriate expiration times
""",
            "users": """# User Management

## Overview
CRUD operations for user entities.

## Database Schema
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API Endpoints
- GET /users - List all users
- GET /users/:id - Get user by ID
- POST /users - Create new user
- PUT /users/:id - Update user
- DELETE /users/:id - Delete user

## Implementation Example
```python
from models import User

def create_user(email, password):
    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user
```
""",
            "errors": """# Error Handling

## Error Response Format
```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "details": {}
    }
}
```

## Common Error Codes
- 400 BAD_REQUEST - Invalid input
- 401 UNAUTHORIZED - Missing/invalid token
- 403 FORBIDDEN - Insufficient permissions
- 404 NOT_FOUND - Resource not found
- 500 INTERNAL_ERROR - Server error

## Implementation
```python
class APIError(Exception):
    def __init__(self, code, message, status_code=400):
        self.code = code
        self.message = message
        self.status_code = status_code

@app.errorhandler(APIError)
def handle_api_error(error):
    return jsonify({
        'error': {
            'code': error.code,
            'message': error.message
        }
    }), error.status_code
```
"""
        }
        
        return docs.get(topic, f"# {topic.title()}\n\nDocumentation not available.")
    
    async def initialize(self, topics: List[str]) -> None:
        """Initialize documentation for all topics"""
        print(f"\n🚀 Initializing documentation in {self.project_dir}/docs/")
        print(f"📡 Using server: {self.server_name}")
        print()
        
        for topic in topics:
            content = await self.fetch_topic_docs(topic)
            
            # Save to file
            output_file = self.docs_dir / f"{topic}.md"
            with open(output_file, 'w') as f:
                f.write(content)
            
            print(f"  ✓ Created {output_file}")
        
        # Create index file
        await self._create_index(topics)
        
        print(f"\n✅ Documentation initialized successfully!")
        print(f"\n📚 Documentation available in: {self.docs_dir}/")
    
    async def _create_index(self, topics: List[str]) -> None:
        """Create index file for documentation"""
        index_content = f"""# Project Documentation

Auto-generated from MCP server: {self.server_name}

## Topics

"""
        for topic in topics:
            index_content += f"- [{topic.title()}]({topic}.md)\n"
        
        index_content += """
## Updating Documentation

To update this documentation, run:
```bash
python scripts/sync_docs.py
```
"""
        
        index_file = self.docs_dir / "README.md"
        with open(index_file, 'w') as f:
            f.write(index_content)
        
        print(f"  ✓ Created {index_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Initialize project documentation from MCP server"
    )
    
    parser.add_argument(
        '--project-dir',
        type=Path,
        default=Path('.'),
        help='Project directory (default: current directory)'
    )
    
    parser.add_argument(
        '--server',
        required=True,
        help='MCP server name from configuration'
    )
    
    parser.add_argument(
        '--topics',
        help='Comma-separated list of topics (e.g., "authentication,users,errors")'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interactive topic selection'
    )
    
    args = parser.parse_args()
    
    # Determine topics
    if args.interactive:
        print("Available topics:")
        available_topics = [
            "authentication",
            "users",
            "errors",
            "api-reference",
            "database",
            "deployment"
        ]
        
        for i, topic in enumerate(available_topics, 1):
            print(f"  {i}. {topic}")
        
        selection = input("\nSelect topics (comma-separated numbers): ").strip()
        indices = [int(x.strip()) - 1 for x in selection.split(',')]
        topics = [available_topics[i] for i in indices if 0 <= i < len(available_topics)]
    
    elif args.topics:
        topics = [t.strip() for t in args.topics.split(',')]
    
    else:
        print("Error: Either --topics or --interactive must be specified")
        return 1
    
    # Initialize documentation
    initializer = ProjectDocsInitializer(args.project_dir, args.server)
    asyncio.run(initializer.initialize(topics))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
