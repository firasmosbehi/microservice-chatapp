# ChatApp Microservices with Frontend

A polyglot microservices chat application featuring five independently deployable services with real-time messaging capabilities.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Services](#services)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Deployment](#deployment)

## Architecture Overview

This application implements a hub-and-spoke microservices architecture with the Gateway Service acting as the central coordinator:

### Service Communication Patterns

**Authentication Flow:**
```
Client → Gateway(/api/auth/login) → User Service → Gateway → Client(JWT)
```

**Real-time Chat Flow:**
```
Client → Gateway(WebSocket) → Chat Service(memory) ↔ Message Service(PostgreSQL)
                                   ↓
                            Broadcast to connected clients
```

**Message Persistence:**
```
Chat Service → Message Service(HTTP) → PostgreSQL
```

### Core Technologies
- **Frontend**: React/Vite (Port 3000)
- **Gateway**: Rust/Actix-web (Port 8000)
- **User Service**: Node.js/Express (Port 3001) with MongoDB
- **Chat Service**: Python/FastAPI (Port 3002) with WebSocket
- **Message Service**: Go/Gin (Port 3003) with PostgreSQL

## Services

| Service | Language | Port | Description |
|---------|----------|------|-------------|
| Frontend Service | React/Vite | 3000 | Single-page application with real-time chat interface |
| Gateway Service | Rust/Actix-web | 8000 | Central API gateway and reverse proxy |
| User Service | Node.js/Express | 3001 | User authentication and profile management |
| Chat Service | Python/FastAPI | 3002 | Real-time WebSocket-based chat functionality |
| Message Service | Go/Gin | 3003 | Persistent message storage in PostgreSQL |

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd ci

# Start all services with Docker Compose
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### Access Points
- **Frontend UI**: http://localhost:3000
- **Gateway API**: http://localhost:8000
- **Individual services**: Available on their respective ports

## Development Setup

### Prerequisites
- Docker and Docker Compose
- Node.js 16+ (for user-service development)
- Python 3.8+ (for chat-service development)
- Go 1.19+ (for message-service development)
- Rust/Cargo (for gateway-service development)

### Local Development Without Docker

For working on individual services locally while keeping others in Docker:

```bash
# Stop the service you want to develop locally
docker-compose stop user-service

# Navigate to service directory and start locally
cd app/user-service
npm install
npm run dev

# Other services remain running in Docker
docker-compose start
```

### Environment Variables

Each service expects specific environment variables. See [Development Workflows](#development-workflows) section for detailed configuration.

## API Documentation

### Gateway Service API (Port 8000)
**Base URL:** `http://localhost:8000`

Routing paths:
- `/api/auth/*` → User Service (3001) - Authentication endpoints
- `/api/users/*` → User Service (3001) - User management
- `/api/chat/*` → Chat Service (3002) - Real-time chat functionality
- `/api/messages/*` → Message Service (3003) - Message persistence

Additional endpoints:
- `GET /health` - System health check with service status
- `GET /` - Gateway index page

### User Service API (Port 3001)
**Base URL:** `http://localhost:3001/api`

Key endpoints:
- `POST /register` - User registration with email verification
- `POST /login` - User authentication returning JWT tokens
- `GET /profile` - Get authenticated user profile (requires token)
- `PUT /profile` - Update user profile information

### Chat Service API (Port 3002)
**Base URL:** `http://localhost:3002/api`

WebSocket endpoints:
- `ws://localhost:3002/ws/{room_id}` - Real-time chat WebSocket connection

HTTP endpoints:
- `POST /rooms` - Create chat rooms
- `GET /rooms/{room_id}` - Get room information
- `POST /rooms/{room_id}/join` - Join a chat room

### Message Service API (Port 3003)
**Base URL:** `http://localhost:3003/api`

Endpoints:
- `GET /messages/room/{room_id}` - Retrieve message history for a room
- `POST /messages` - Store new messages
- `PUT /messages/{message_id}/read` - Mark messages as read

## Testing

### Running Tests

#### All Services Tests
```bash
# Sequential execution (recommended for CI)
cd app
python run_microservice_tests.py

# Parallel execution (faster for local development)
python run_microservice_tests.py --parallel
```

#### Individual Service Tests

**User Service (Node.js)**
```bash
cd app/user-service
node tests/run-tests.js
```

**Chat Service (Python)**
```bash
cd app/chat-service
# Fast unit tests
poetry run python run_tests_fast.py fast

# Full test suite with coverage
poetry run python run_tests_fast.py coverage

# Run all tests (traditional runner)
poetry run python run_tests.py

# Run specific test modes
poetry run python run_tests_fast.py security  # Security scanning
poetry run python run_tests_fast.py lint      # Code quality
poetry run python run_tests_fast.py type-check # Type checking

# Run tests with pytest directly
poetry run pytest tests/unit/test_api.py tests/unit/test_services.py tests/unit/test_models.py -v
poetry run pytest tests/unit/ -v --cov=chat_app
poetry run pytest tests/integration/ -v

# Security Testing Commands
# Check for security vulnerabilities in dependencies
poetry run python -c "
import subprocess
import sys
try:
    # Try to run safety check
    result = subprocess.run([sys.executable, '-m', 'safety', 'check'], 
                          capture_output=True, text=True, cwd='.')
    if result.returncode == 0:
        print('✅ Safety check passed')
    else:
        print('⚠️  Safety check found potential issues:')
        print(result.stdout)
except FileNotFoundError:
    print('ℹ️  Safety not installed. Install with: pip install safety')
    print('Then run: poetry run safety check')
"

# Basic security scanning with built-in tools
poetry run python -c "
import ast
import os
from pathlib import Path

def check_security_issues(file_path):
    with open(file_path, 'r') as f:
        try:
            tree = ast.parse(f.read())
            issues = []
            for node in ast.walk(tree):
                # Check for eval usage
                if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'eval':
                    issues.append('Use of eval() found')
                # Check for exec usage
                if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'exec':
                    issues.append('Use of exec() found')
            return issues
        except SyntaxError:
            return ['Syntax error in file']

# Scan Python files for basic security issues
chat_app_dir = Path('chat_app')
issues_found = []
for py_file in chat_app_dir.rglob('*.py'):
    file_issues = check_security_issues(py_file)
    if file_issues:
        issues_found.extend([f'{py_file}: {issue}' for issue in file_issues])

if issues_found:
    print('⚠️  Security issues found:')
    for issue in issues_found:
        print(f'  - {issue}')
else:
    print('✅ No basic security issues found in scan')
"

# Linting and Code Quality Commands
# Flake8 linting (matches run_tests.py configuration)
poetry run flake8 chat_app/ --max-line-length=100 --extend-ignore=E203,W503,E501,W292,W291,W293,E722,E128,F841,F401

# Black code formatting check
poetry run black --check chat_app/

# MyPy type checking
poetry run mypy chat_app/

# Run all available quality checks together
poetry run python -c "
import subprocess
import sys

checks = [
    ('Flake8 linting', ['flake8', 'chat_app/', '--max-line-length=100']),
    ('Black formatting', ['black', '--check', 'chat_app/']),
    ('MyPy type checking', ['mypy', 'chat_app/'])
]

passed = 0
total = len(checks)

for name, cmd in checks:
    try:
        result = subprocess.run(['poetry', 'run'] + cmd, 
                              capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            print(f'✅ {name} passed')
            passed += 1
        else:
            print(f'❌ {name} failed:')
            print(result.stdout[:200] + '...' if len(result.stdout) > 200 else result.stdout)
    except FileNotFoundError as e:
        print(f'⚠️  {name} tool not found: {e}')
    except Exception as e:
        print(f'⚠️  {name} error: {e}')

print(f'\n📊 Quality checks: {passed}/{total} passed')
"

# Installing Additional Security Tools (Optional)
# To add advanced security scanning capabilities, install these tools:
# 
# poetry add --group dev bandit safety
#
# Then you can run:
# poetry run bandit -r chat_app/ -ll
# poetry run safety check
# poetry run pip-audit
```

**Message Service (Go)**
```bash
cd app/message-service
./tests/run_tests.sh
```

**Gateway Service (Rust)**
```bash
cd app/gateway-service
cargo test
```

### Test Coverage

Each service includes comprehensive tests for:
- API endpoint validation
- Business logic testing
- Integration scenarios
- Error handling
- Security scanning
- Code quality checks

### Test Organization

```
app/chat-service/
├── chat_app/                   # Main application package
│   ├── __init__.py            # Package initialization
│   ├── app.py                 # FastAPI application setup
│   ├── models.py              # Pydantic data models
│   ├── services.py            # Business logic layer
│   ├── routes.py              # API endpoints
│   └── websocket.py           # WebSocket handlers
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   │   ├── test_api.py        # API endpoint tests
│   │   ├── test_models.py     # Model validation tests
│   │   ├── test_services.py   # Business logic tests
│   │   ├── test_code_coverage.py # Code coverage tests
│   │   ├── test_full_coverage.py # Full coverage tests
│   │   └── test_complete_coverage.py # Complete coverage tests
│   ├── integration/           # Integration tests
│   │   └── test_integration.py # Integration tests
│   ├── security/              # Security tests
│   │   └── test_security.py   # Security vulnerability tests
│   ├── linting/               # Linting tests
│   │   └── test_linting.py    # Code quality tests
│   └── conftest.py            # Test configuration
├── scripts/                   # Scripts
│   ├── run_tests.py           # Traditional test runner
│   └── run_tests_fast.py      # Fast test runner
├── main.py                    # Application entry point
├── pyproject.toml             # Poetry configuration
├── requirements.txt           # Python dependencies
└── NAMING_CONVENTIONS.md      # Naming conventions documentation
```

## CI/CD Pipeline

The repository uses GitHub Actions for continuous integration with automated testing and security scanning:

### Pipeline Stages

1. **Testing Stage** - Runs on every push/PR to `main` and `dev` branches:
   - Unit tests execution
   - Integration tests
   - Security vulnerability scanning
   - Code quality and linting checks
   - Type checking

2. **Docker Build & Push Stage** - Runs only on pushes to `main` branch:
   - Builds Docker images for all services
   - Pushes to GitHub Container Registry (GHCR)
   - Supports multi-architecture builds (amd64, arm64)

### CI Caching Strategy

Comprehensive caching is implemented to optimize build times:

**Dependency Caching:**
- Poetry dependencies for Python services
- Node.js modules for JavaScript services
- Go modules for Go services
- Cargo registry for Rust services

**Docker Layer Caching:**
- Intermediate build layers
- Multi-stage build optimization

**Performance Improvements:**
| Service | Without Cache | With Cache | Improvement |
|---------|---------------|------------|-------------|
| Gateway (Rust) | 30+ minutes | 1-2 minutes | 95%+ faster |
| Chat (Python) | 2-3 minutes | 30-60 seconds | 75%+ faster |
| Frontend/User (Node.js) | 1-2 minutes | 20-40 seconds | 75%+ faster |
| Message (Go) | 1-2 minutes | 30-60 seconds | 75%+ faster |

## Deployment

### Production Considerations

**Environment Configuration:**
- Use proper environment variables for production secrets
- Configure appropriate JWT token expiration times
- Set up monitoring and alerting for service health

**Scaling Strategies:**
- **Gateway Service**: Can be scaled horizontally behind a load balancer
- **User Service**: Stateful due to MongoDB; use replica sets for scaling
- **Chat Service**: In-memory state limits horizontal scaling; consider sticky sessions
- **Message Service**: PostgreSQL allows read replicas for scaling reads
- **Frontend Service**: Stateless and easily scalable

**Security Best Practices:**
- Rotate JWT secrets regularly
- Use HTTPS/TLS for all service communications
- Implement proper CORS policies
- Regular security scanning in CI pipeline

### Monitoring and Debugging

**Service Health Checks:**
```bash
# Check individual service health
curl http://localhost:8000/health          # Gateway + all services
curl http://localhost:3001/                # User service
curl http://localhost:3002/health          # Chat service  
curl http://localhost:3003/health          # Message service
```

**Log Analysis:**
```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f user-service

# Search logs for specific patterns
docker-compose logs | grep "ERROR"
```

### Database Access

```bash
# Check MongoDB data
docker-compose exec mongo mongosh chatapp-users --eval "db.users.find()"

# Check PostgreSQL data  
docker-compose exec postgres psql -U postgres -d chatapp_messages -c "SELECT * FROM messages LIMIT 10;"
```

## Development Workflows

### Multi-Service Development

When working across multiple services:

1. **Start dependencies in Docker:**
   ```bash
   docker-compose up -d mongo postgres
   ```

2. **Develop one service locally while others run in containers**

3. **Use environment variables to point to Docker services**

### Service Interaction Testing

```bash
# Test gateway routing
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"password123"}'

# Test direct service access (for debugging)
curl http://localhost:3001/api/users
```

### Common Development Commands

See [AGENTS.md](AGENTS.md) for comprehensive development commands and troubleshooting guides.

## Troubleshooting

### Common Issues

**Authentication Failures:**
- Check JWT secret consistency across services
- Verify token expiration times
- Confirm user-service is reachable from gateway

**WebSocket Connection Issues:**
- Ensure proper CORS configuration
- Check firewall/port accessibility
- Verify load balancer WebSocket support

**Database Connection Problems:**
- Confirm database containers are running
- Check connection string configurations
- Validate database credentials and permissions

**Docker Build Issues (Rust):**
- If encountering Rust version compatibility errors, update the Dockerfile base image to a newer Rust version (1.83+)
- Alternatively, pin problematic dependencies to older versions that support the current Rust version

### Debugging Strategies

1. **Check gateway logs for routing errors:**
   ```bash
   docker-compose logs gateway-service
   ```

2. **Verify service health:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Test individual services directly when needed**

## Repository Structure

```
.
├── app/
│   ├── docker-compose.yml          # Main orchestration file
│   ├── frontend-service/           # React/Vite SPA
│   ├── gateway-service/            # Rust API gateway/load balancer
│   ├── user-service/               # Node.js user management [MongoDB]
│   ├── chat-service/               # Python real-time chat
│   │   ├── chat_app/              # Application code
│   │   ├── tests/                 # Test suite
│   │   │   ├── unit/              # Unit tests
│   │   │   ├── integration/       # Integration tests
│   │   │   ├── security/          # Security tests
│   │   │   └── linting/           # Linting tests
│   │   ├── scripts/               # Test runners
│   │   │   ├── run_tests.py       # Traditional runner
│   │   │   └── run_tests_fast.py  # Fast runner
│   │   └── NAMING_CONVENTIONS.md  # Naming conventions
│   └── message-service/            # Go message persistence [PostgreSQL]
├── .github/
│   └── workflows/
│       └── ci.yml                  # CI/CD pipeline configuration
├── AGENTS.md                       # Development guide and architecture documentation
└── README.md                       # This file
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.