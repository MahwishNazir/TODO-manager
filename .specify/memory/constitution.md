<!--
Sync Impact Report:
Version Change: [UNVERSIONED] → 1.0.0
Modified Principles: N/A (initial constitution)
Added Sections:
  - Core Principles (7 principles)
  - Phased Architecture Requirements
  - Technology Stack Standards
  - Development Workflow
  - Governance
Templates Requiring Updates: ✅ All templates aligned with constitution
Follow-up TODOs: None
-->

# TODO Application Constitution

## Core Principles

### I. Phased Development Approach (MANDATORY)

The TODO application MUST be developed in five sequential phases, each fully functional and deployable before proceeding to the next:

- **Phase I**: In-Memory Python Console App (Foundation)
- **Phase II**: Full-Stack Web Application (Scalability)
- **Phase III**: AI-Powered Todo Chatbot (Intelligence)
- **Phase IV**: Local Kubernetes Deployment (Orchestration)
- **Phase V**: Advanced Cloud Deployment (Production-Ready)

Each phase MUST:
- Be fully tested and verified working before advancing
- Preserve all functionality from previous phases
- Follow incremental feature rollout (Basic → Intermediate → Advanced)
- Maintain backward compatibility in data structures

**Rationale**: Phased development reduces risk, enables early validation, and ensures each technology layer is proven before adding complexity.

### II. Spec-Driven Development (NON-NEGOTIABLE)

ALL development MUST follow the SDD workflow:
1. **Specification** (`specs/<feature>/spec.md`) - Define requirements, success criteria, constraints
2. **Planning** (`specs/<feature>/plan.md`) - Architecture decisions, API contracts, NFRs
3. **Tasks** (`specs/<feature>/tasks.md`) - Testable task breakdown with acceptance criteria
4. **Implementation** - Execute tasks with verification checkpoints

**Enforcement**:
- No code written before spec/plan/tasks are approved
- Every change references a spec document
- Prompt History Records (PHRs) created for every user interaction
- Architectural Decision Records (ADRs) required for significant decisions

**Rationale**: Spec-first development prevents scope creep, enables better planning, and creates documentation as a byproduct of development.

### III. Test-First Development (NON-NEGOTIABLE)

TDD cycle MUST be followed strictly:
1. Write tests for feature/task
2. User approves test cases
3. Verify tests fail (Red)
4. Implement minimal code to pass (Green)
5. Refactor while maintaining green tests
6. Verify working at end of each step

**Requirements**:
- Unit tests for all business logic
- Integration tests for API contracts and database interactions
- End-to-end tests for critical user workflows
- Minimum 80% code coverage for production code

**Rationale**: Test-first ensures correctness, prevents regressions, and serves as executable documentation.

### IV. Separation of Concerns

Frontend and backend MUST be developed and deployed independently:

**Directory Structure**:
```
/frontend    - All UI code (Next.js for Phase II+)
/backend     - All server code (Python/FastAPI for Phase I-II)
/shared      - Common types, schemas, contracts
```

**Contracts**:
- API contracts defined in OpenAPI/JSON Schema
- Shared data models documented in spec
- Clear interface boundaries with versioning

**Rationale**: Independent deployment, technology flexibility, parallel development, and easier testing.

### V. Feature Tiering and Progressive Enhancement

Features MUST be implemented in three tiers per phase:

**Basic Level** (Core MVP - MUST implement first):
- Add Task
- Delete Task
- Update Task
- View Task List
- Mark as Complete/Incomplete

**Intermediate Level** (Organization - Second priority):
- Assign Priorities (high/medium/low)
- Search & Filter (by priority, status, date)
- Auto-sort (by due date, priority)

**Advanced Level** (Intelligence - Final enhancement):
- Recurring Tasks (auto-reschedule)
- Due Dates & Time Reminders
- Browser/system notifications

**Enforcement**: Each tier MUST be fully working and tested before advancing to next tier within a phase.

**Rationale**: Ensures we always have a working product; reduces risk; enables early user feedback.

### VI. Technology Stack Discipline

Each phase MUST use its designated technology stack without deviation:

**Phase I**:
- Language: Python 3.10+
- Storage: In-memory (dict/list structures)
- Interface: Console/CLI
- Tools: Claude Code, Spec-Kit Plus
- Testing: pytest

**Phase II**:
- Frontend: Next.js 14+ (TypeScript, React)
- Backend: FastAPI (Python 3.10+)
- ORM: SQLModel
- Database: Neon DB (PostgreSQL)
- Testing: pytest (backend), Jest/Vitest (frontend)

**Phase III**:
- AI Framework: OpenAI ChatKit
- Agent Framework: Agents SDK
- MCP Integration: Official MCP SDK
- Existing stack preserved from Phase II

**Phase IV**:
- Containerization: Docker
- Orchestration: Minikube (local Kubernetes)
- Package Manager: Helm
- Tools: kubectl-ai, kagent

**Phase V**:
- Messaging: Kafka
- Service Mesh: Dapr
- Cloud Platform: DigitalOcean DOKS
- Existing orchestration from Phase IV

**Requirements**:
- All dependencies declared in phase-specific manifests
- No technology substitutions without constitutional amendment
- Version pinning for reproducibility

**Rationale**: Technology discipline prevents analysis paralysis, ensures learnings transfer across phases, and maintains focus.

### VII. Data Integrity and Migration

Data MUST be preserved and migrated across phases:

**Phase Transitions**:
- Phase I → II: Export JSON → Import to Neon DB
- Phase II → III: Schema extension (preserve existing)
- Phase III → IV: Database state maintained in persistent volumes
- Phase IV → V: Cloud migration with zero data loss

**Requirements**:
- Migration scripts tested before deployment
- Rollback procedures documented
- Data validation post-migration
- Backup strategy at each phase

**Rationale**: Protect user data, enable seamless transitions, maintain trust.

## Phased Architecture Requirements

### Phase I: Foundation (In-Memory Python Console)

**Objectives**: Prove core business logic, establish testing patterns, validate UX flows.

**Deliverables**:
- Fully functional CRUD operations
- In-memory task storage (Python data structures)
- Console-based UI with clear menu system
- Complete test suite (pytest)
- Data export capability (JSON)

**Success Criteria**:
- All Basic tier features working
- Test coverage ≥ 80%
- User can perform complete workflows via console
- Data persists during session (memory only)

### Phase II: Scalability (Full-Stack Web)

**Objectives**: Add persistence, web UI, multi-user support, RESTful API.

**Deliverables**:
- RESTful API (FastAPI) with OpenAPI docs
- Web UI (Next.js with responsive design)
- PostgreSQL database (Neon DB)
- User authentication and authorization
- API versioning (v1)

**Success Criteria**:
- All Phase I features + web interface
- Data persists across sessions
- API documented and tested
- Frontend/backend deployable independently

### Phase III: Intelligence (AI-Powered Chatbot)

**Objectives**: Add natural language interaction, smart suggestions, context awareness.

**Deliverables**:
- Conversational interface for task management
- NLP-based task parsing ("Remind me to call John tomorrow at 3pm")
- Smart suggestions (priorities, due dates)
- MCP server integration for tool use

**Success Criteria**:
- Users can manage tasks via chat
- AI correctly interprets task intent
- All Phase II features accessible via chat or UI

### Phase IV: Orchestration (Local Kubernetes)

**Objectives**: Containerize, orchestrate, establish deployment patterns.

**Deliverables**:
- Docker images for all services
- Kubernetes manifests (deployments, services, ingress)
- Helm charts for installation
- Local development cluster (Minikube)

**Success Criteria**:
- One-command deployment to local K8s
- Services auto-scale based on load
- Health checks and monitoring operational

### Phase V: Production-Ready (Cloud Deployment)

**Objectives**: Production deployment, event streaming, observability, resilience.

**Deliverables**:
- Kafka event bus for async processing
- Dapr service mesh integration
- DigitalOcean DOKS cluster deployment
- Production monitoring and alerting
- CI/CD pipeline

**Success Criteria**:
- Production-grade reliability (99.9% uptime)
- Horizontal scaling operational
- Observability stack deployed (logs, metrics, traces)
- Automated deployments working

## Technology Stack Standards

### Code Quality

**Python**:
- Style: PEP 8 compliance (black formatter)
- Type hints: Required for all public functions
- Docstrings: Google style for all modules/classes/functions
- Linting: pylint, mypy

**TypeScript/JavaScript**:
- Style: ESLint + Prettier
- Type safety: Strict mode enabled
- Framework conventions: Next.js App Router, React hooks

### Security

**Authentication & Authorization**:
- Phase II+: JWT-based auth with secure refresh tokens
- Password hashing: bcrypt/argon2
- HTTPS only in production
- CORS properly configured

**Data Protection**:
- Input validation on all endpoints
- SQL injection prevention (parameterized queries via SQLModel)
- XSS prevention (framework defaults + CSP headers)
- Secrets management (environment variables, never committed)

### Performance

**Response Time Targets**:
- API endpoints: p95 < 200ms
- Database queries: p95 < 100ms
- UI interactions: < 100ms perceived latency

**Resource Limits** (Phase IV+):
- Backend containers: 512MB RAM, 0.5 CPU
- Frontend containers: 256MB RAM, 0.25 CPU
- Database: Connection pooling (max 20 connections)

### Observability

**Logging**:
- Structured JSON logs (all phases)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Correlation IDs for request tracing

**Metrics** (Phase IV+):
- RED metrics: Request rate, Error rate, Duration
- Resource metrics: CPU, Memory, Disk, Network

**Tracing** (Phase V):
- Distributed tracing via OpenTelemetry
- All service-to-service calls traced

## Development Workflow

### Spec-Driven Cycle

1. **User Request** → Clarify requirements, identify phase/tier
2. **Create/Update Spec** → Document in `specs/<feature>/spec.md`
3. **Architectural Planning** → Create `specs/<feature>/plan.md` with ADRs
4. **Task Breakdown** → Generate `specs/<feature>/tasks.md` with test cases
5. **Implementation** → Execute tasks following TDD (Red-Green-Refactor)
6. **Verification** → Confirm working at task completion
7. **Documentation** → Create PHR, update ADRs if needed
8. **User Checkpoint** → Demo working feature, get approval to proceed

### Verification Checkpoints

**Task Level**:
- Tests pass (green)
- Code reviewed (self-review minimum)
- Acceptance criteria met

**Feature Level**:
- All tasks completed
- Integration tests pass
- User acceptance confirmed

**Phase Level**:
- All tiers working (Basic → Intermediate → Advanced)
- Migration path to next phase documented
- Deployment tested in target environment

### Prompt History Records (PHR)

**Mandatory Creation**:
- After every user prompt/request
- Before and after significant decisions
- During debugging sessions
- Post-implementation summaries

**Routing** (under `history/prompts/`):
- Constitution changes → `constitution/`
- Feature work → `<feature-name>/`
- General work → `general/`

**Required Fields**:
- Full user prompt (verbatim, not truncated)
- Assistant response summary
- Stage (spec/plan/tasks/red/green/refactor/etc.)
- Files modified, tests run
- Links to spec/ADR/PR

### Architectural Decision Records (ADR)

**Trigger Test** (all must be true):
- **Impact**: Long-term consequences (framework, data model, API, security, platform)
- **Alternatives**: Multiple viable options considered
- **Scope**: Cross-cutting, influences system design

**Required Content**:
- Context and problem statement
- Decision drivers
- Options considered with pros/cons
- Chosen option with rationale
- Consequences (positive and negative)

**Location**: `history/adr/<sequential-number>-<slug>.md`

## Governance

### Amendment Process

**Constitutional amendments require**:
1. Documented rationale in ADR
2. Impact analysis on existing specs/plans/tasks
3. Migration plan for affected code
4. Version bump following semver:
   - **MAJOR**: Principle removal or incompatible changes
   - **MINOR**: New principles or material expansions
   - **PATCH**: Clarifications, typo fixes, non-semantic changes

### Compliance

**Enforcement**:
- All PRs/changes verified against constitution
- Claude Code agent enforces workflow automatically
- Deviations require explicit justification and approval

**Conflict Resolution**:
- Constitution supersedes all other guidance
- Ambiguities resolved in favor of user intent
- Updates made promptly when conflicts discovered

### Reviews

**Checkpoints**:
- End of each phase: Constitutional review
- After major architectural decisions: Alignment check
- Quarterly: Principle relevance review

### Runtime Guidance

For day-to-day development practices, refer to `CLAUDE.md` which provides detailed agent instructions aligned with this constitution.

**Version**: 1.0.0 | **Ratified**: 2026-01-10 | **Last Amended**: 2026-01-10
