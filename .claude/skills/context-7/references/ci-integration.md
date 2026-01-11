# CI/CD Integration

Guide for integrating MCP documentation retrieval into CI/CD pipelines with Claude Code.

## Use Cases

1. **Documentation Validation** - Verify code matches API specs
2. **Auto-generated Docs** - Keep docs in sync with code
3. **Code Review Automation** - Check against best practices
4. **Test Data Generation** - Generate test cases from API specs
5. **Contract Testing** - Validate API contracts

## GitHub Actions

### Validate API Implementation

```yaml
name: Validate API Against Docs

on:
  pull_request:
    paths:
      - 'src/api/**'
      - 'tests/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install claude-code-mcp
      
      - name: Configure MCP
        env:
          MCP_API_KEY: ${{ secrets.MCP_API_KEY }}
        run: |
          python scripts/setup_mcp.py \
            --server mcp://docs.example.com \
            --name official-docs \
            --auth-type api_key \
            --api-key $MCP_API_KEY
      
      - name: Fetch API Specification
        run: |
          python mcp_client.py fetch docs://api/spec \
            --output spec.json
      
      - name: Validate Implementation
        run: |
          python scripts/validate_api.py \
            --spec spec.json \
            --implementation src/api/
```

### Auto-update Documentation

```yaml
name: Update Project Documentation

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  update-docs:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Configure MCP
        env:
          MCP_API_KEY: ${{ secrets.MCP_API_KEY }}
        run: |
          python scripts/setup_mcp.py \
            --server mcp://docs.example.com \
            --name official-docs \
            --auth-type api_key \
            --api-key $MCP_API_KEY
      
      - name: Update Documentation
        run: |
          python scripts/sync_docs.py \
            --project-dir . \
            --force
      
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: 'docs: update from MCP server'
          title: 'Update documentation from MCP'
          body: 'Automated documentation update from MCP server'
          branch: docs-update
```

## GitLab CI

### Documentation Pipeline

```yaml
# .gitlab-ci.yml

stages:
  - validate
  - test
  - deploy

variables:
  MCP_SERVER: "mcp://docs.example.com"

validate_api:
  stage: validate
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - python scripts/setup_mcp.py --server $MCP_SERVER --name official-docs --auth-type api_key --api-key $MCP_API_KEY
    - python mcp_client.py fetch docs://api/spec --output spec.json
    - python scripts/validate_api.py --spec spec.json --implementation src/
  only:
    - merge_requests
    - main

update_docs:
  stage: deploy
  image: python:3.11
  script:
    - python scripts/setup_mcp.py --server $MCP_SERVER --name official-docs --auth-type api_key --api-key $MCP_API_KEY
    - python scripts/sync_docs.py --project-dir . --force
    - git config user.email "ci@example.com"
    - git config user.name "GitLab CI"
    - git add docs/
    - git commit -m "docs: auto-update from MCP" || true
    - git push origin HEAD:docs-update
  only:
    - schedules
```

## Jenkins

### Jenkinsfile

```groovy
pipeline {
    agent any
    
    environment {
        MCP_API_KEY = credentials('mcp-api-key')
        MCP_SERVER = 'mcp://docs.example.com'
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
                sh """
                    python scripts/setup_mcp.py \
                        --server ${MCP_SERVER} \
                        --name official-docs \
                        --auth-type api_key \
                        --api-key ${MCP_API_KEY}
                """
            }
        }
        
        stage('Fetch Documentation') {
            steps {
                sh 'python mcp_client.py fetch docs://api/spec --output spec.json'
            }
        }
        
        stage('Validate') {
            steps {
                sh 'python scripts/validate_api.py --spec spec.json --implementation src/'
            }
        }
        
        stage('Update Docs') {
            when {
                branch 'main'
            }
            steps {
                sh 'python scripts/sync_docs.py --project-dir . --force'
                sh '''
                    git add docs/
                    git commit -m "docs: auto-update from MCP" || true
                    git push origin HEAD
                '''
            }
        }
    }
    
    post {
        failure {
            mail to: 'team@example.com',
                 subject: "MCP Documentation Pipeline Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                 body: "Check console output at ${env.BUILD_URL}"
        }
    }
}
```

## CircleCI

```yaml
# .circleci/config.yml

version: 2.1

jobs:
  validate-api:
    docker:
      - image: python:3.11
    steps:
      - checkout
      - run:
          name: Install dependencies
          command: pip install -r requirements.txt
      - run:
          name: Configure MCP
          command: |
            python scripts/setup_mcp.py \
              --server mcp://docs.example.com \
              --name official-docs \
              --auth-type api_key \
              --api-key $MCP_API_KEY
      - run:
          name: Fetch and validate
          command: |
            python mcp_client.py fetch docs://api/spec --output spec.json
            python scripts/validate_api.py --spec spec.json --implementation src/

  update-docs:
    docker:
      - image: python:3.11
    steps:
      - checkout
      - run:
          name: Configure MCP
          command: |
            python scripts/setup_mcp.py \
              --server mcp://docs.example.com \
              --name official-docs \
              --auth-type api_key \
              --api-key $MCP_API_KEY
      - run:
          name: Update documentation
          command: python scripts/sync_docs.py --project-dir . --force

workflows:
  version: 2
  validate:
    jobs:
      - validate-api
  
  weekly-docs-update:
    triggers:
      - schedule:
          cron: "0 0 * * 0"
          filters:
            branches:
              only:
                - main
    jobs:
      - update-docs
```

## Docker Integration

### Dockerfile for CI

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP client scripts
COPY scripts/ ./scripts/

# Configure MCP (will be overridden by environment variables)
ENV MCP_CONFIG_DIR=/root/.claude-code
ENV MCP_CACHE_DIR=/root/.claude-code/cache

# Default command
CMD ["python", "mcp_client.py", "list"]
```

### Docker Compose for Testing

```yaml
# docker-compose.yml

version: '3.8'

services:
  mcp-client:
    build: .
    environment:
      - MCP_API_KEY=${MCP_API_KEY}
      - MCP_SERVER=mcp://docs.example.com
    volumes:
      - ./src:/app/src
      - ./docs:/app/docs
      - mcp-cache:/root/.claude-code/cache
    command: |
      bash -c "
        python scripts/setup_mcp.py --server $$MCP_SERVER --name official-docs --auth-type api_key --api-key $$MCP_API_KEY &&
        python scripts/sync_docs.py --project-dir /app
      "

volumes:
  mcp-cache:
```

## Pre-commit Hooks

### Validate Before Commit

```bash
# .git/hooks/pre-commit

#!/bin/bash

# Fetch latest API spec
python mcp_client.py fetch docs://api/spec --output /tmp/spec.json

# Validate implementation
python scripts/validate_api.py --spec /tmp/spec.json --implementation src/

if [ $? -ne 0 ]; then
    echo "❌ API validation failed"
    echo "Your implementation doesn't match the API specification"
    exit 1
fi

echo "✅ API validation passed"
```

## Scheduled Jobs

### Cron Job for Documentation Sync

```bash
# Add to crontab: crontab -e

# Sync documentation every Sunday at midnight
0 0 * * 0 cd /path/to/project && python scripts/sync_docs.py --force >> /var/log/mcp-sync.log 2>&1

# Check for documentation updates daily
0 9 * * * cd /path/to/project && python scripts/check_docs_updates.py --notify-if-outdated
```

### Systemd Timer

```ini
# /etc/systemd/system/mcp-docs-sync.timer

[Unit]
Description=MCP Documentation Sync Timer
Requires=mcp-docs-sync.service

[Timer]
OnCalendar=weekly
Persistent=true

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/mcp-docs-sync.service

[Unit]
Description=MCP Documentation Sync Service

[Service]
Type=oneshot
User=developer
WorkingDirectory=/path/to/project
Environment="MCP_API_KEY=your-api-key"
ExecStart=/usr/bin/python3 scripts/sync_docs.py --force
```

## Validation Scripts

### API Validation Script

```python
#!/usr/bin/env python3
"""
Validate API implementation against MCP specification
"""

import json
import sys
from pathlib import Path

def validate_api(spec_file, implementation_dir):
    """Validate API implementation"""
    
    # Load specification
    with open(spec_file) as f:
        spec = json.load(f)
    
    errors = []
    
    # Validate endpoints
    for endpoint in spec.get('endpoints', []):
        # Check if endpoint exists in implementation
        # This is simplified - real validation would be more complex
        
        method = endpoint['method']
        path = endpoint['path']
        
        print(f"Validating: {method} {path}")
        
        # Check implementation file exists
        # Check parameters match
        # Check response format matches
        
    if errors:
        print("\n❌ Validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("\n✅ All validations passed")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--spec', required=True)
    parser.add_argument('--implementation', required=True)
    
    args = parser.parse_args()
    
    success = validate_api(args.spec, args.implementation)
    sys.exit(0 if success else 1)
```

## Monitoring and Notifications

### Slack Notification

```python
import requests

def notify_slack(webhook_url, message):
    """Send notification to Slack"""
    payload = {
        "text": message,
        "username": "MCP Bot",
        "icon_emoji": ":robot_face:"
    }
    
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200

# Usage in CI
if docs_updated:
    notify_slack(
        os.environ['SLACK_WEBHOOK'],
        "📚 Documentation updated from MCP server"
    )
```

## Best Practices

1. **Cache MCP responses** - Avoid rate limits in CI
2. **Use specific versions** - Pin MCP server versions for reproducibility
3. **Secure credentials** - Use secrets management (GitHub Secrets, etc.)
4. **Fail fast** - Validate early in pipeline
5. **Notify on failures** - Alert team when validation fails
6. **Version control docs** - Track documentation changes
7. **Test locally first** - Validate CI scripts before pushing
8. **Monitor API changes** - Alert on breaking changes
9. **Keep logs** - Store MCP interaction logs for debugging
10. **Regular updates** - Schedule documentation refreshes
