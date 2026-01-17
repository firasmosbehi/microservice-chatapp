# AGENTS.md

This file provides guidance to Qoder (qoder.com) when working with code in this repository.

## Key Architectural Insights

### Service Communication Architecture
The microservices architecture follows a hub-and-spoke pattern with the Gateway Service acting as the central coordinator:

1. **Client → Gateway → Backend Services**: All client requests route through the Rust-based Gateway Service
2. **JWT Token Validation**: Gateway handles authentication and forwards validated requests with user context
3. **Service Isolation**: Each service operates independently with its own database and business logic
4. **WebSocket Proxying**: Real-time connections are proxied through the gateway to maintain authentication context

### Data Flow Patterns

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

## Codebase Architecture Overview

This is a polyglot microservices chat application featuring five independently deployable services:

**Frontend Service (React/Vite)** - Port 3000
- Single-page application with real-time chat interface
- Communicates exclusively through Gateway Service API
- Built with modern React hooks and Vite for fast development

**Gateway Service (Rust/Actix-web)** - Port 8000  
- Central API gateway and reverse proxy
- Handles JWT authentication and authorization
- Routes requests to appropriate backend services
- Implements CORS, rate limiting, and centralized logging

**User Service (Node.js/Express)** - Port 3001
- User authentication and profile management
- MongoDB for user data persistence
- JWT token generation and validation
- Email verification and password reset flows

**Chat Service (Python/FastAPI)** - Port 3002
- Real-time WebSocket-based chat functionality
- In-memory state management for active connections
- Typing indicators and presence detection
- Message broadcasting and room management

**Message Service (Go/Gin)** - Port 3003
- Persistent message storage in PostgreSQL
- Read receipt tracking and message threading
- Efficient database queries with proper indexing
- Soft-delete pattern for message management

## Core Service APIs and Endpoints

### User Service API (Port 3001)
**Base URL:** `http://localhost:3001/api`

Key endpoints:
- `POST /register` - User registration with email verification
- `POST /login` - User authentication returning JWT tokens
- `GET /profile` - Get authenticated user profile (requires token)
- `PUT /profile` - Update user profile information
- `POST /refresh-token` - Refresh expired JWT tokens
- `GET /users` - List users (authenticated)
- `POST /logout` - Invalidate user session

Authentication: JWT tokens issued by this service are validated by the gateway for all protected routes.

### Chat Service API (Port 3002)
**Base URL:** `http://localhost:3002/api`

WebSocket endpoints:
- `ws://localhost:3002/ws/{room_id}` - Real-time chat WebSocket connection

HTTP endpoints:
- `POST /rooms` - Create chat rooms
- `GET /rooms/{room_id}` - Get room information
- `GET /rooms` - List available rooms
- `POST /rooms/{room_id}/join` - Join a chat room
- `POST /rooms/{room_id}/leave` - Leave a chat room
- `POST /rooms/{room_id}/messages` - Send messages to room

Features: Real-time messaging, typing indicators, presence detection, message threading/replies.

### Message Service API (Port 3003)
**Base URL:** `http://localhost:3003/api`

Endpoints:
- `GET /messages/room/{room_id}` - Retrieve message history for a room
- `POST /messages` - Store new messages
- `PUT /messages/{message_id}/read` - Mark messages as read
- `GET /messages/unread/{user_id}` - Get unread message counts
- `DELETE /messages/{message_id}` - Delete messages (soft delete)

Database: PostgreSQL with message persistence, read receipts, and indexing for efficient querying.

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

Features: JWT validation, request routing, CORS handling, rate limiting, centralized logging.

## Development Commands

### Docker Compose Commands
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f frontend-service

# Rebuild and restart services
docker-compose up -d --build

# Fix Docker build issues (Rust version compatibility)
docker-compose build --no-cache gateway-service
```

### Frontend Service (React/Vite) - Port 3000
```bash
# Navigate to frontend service
cd app/frontend-service

# Install dependencies
npm install

# Start development server
npm run start

# Build for production
npm run build

# Preview production build
npm run preview
```

### User Service (Node.js/Express) - Port 3001
```bash
# Navigate to user service
cd app/user-service

# Install dependencies
npm install

# Start development server
npm run dev

# Start production server
npm start

# Run with nodemon for auto-restart
npx nodemon server.js
```

### Chat Service (Python) - Port 3002
```bash
# Navigate to chat service
cd app/chat-service

# Install dependencies using Poetry
poetry install

# Run service with Uvicorn (matches Docker setup)
poetry run python -m uvicorn chat_app.app:app --host 0.0.0.0 --port 3002 --reload

# Alternative: Direct execution (matches app.py)
poetry run python -m chat_app.app

# Run all tests (recommended approach)
poetry run python run_tests.py

# Run optimized fast tests (much quicker)
poetry run python run_tests_optimized.py fast

# Run specific test modes
poetry run python run_tests_optimized.py full      # Full testing suite
poetry run python run_tests_optimized.py coverage  # 100% coverage tests
poetry run python run_tests_optimized.py changed   # Only tests for changed files
poetry run python run_tests_optimized.py lint      # Quick linting
poetry run python run_tests_optimized.py type-check # Type checking

# Run tests with pytest directly
poetry run pytest tests/unit/test_api.py tests/unit/test_services.py tests/unit/test_models.py -v
poetry run pytest tests/unit/ -v --cov=chat_app
poetry run pytest tests/integration/ -v
```

### Message Service (Go) - Port 3003
```bash
# Navigate to message service
cd app/message-service

# Build and run
go run main.go

# Build binary
go build -o message-service

# Format code
go fmt ./...

# Build with race detector
go run -race main.go
```

### Gateway Service (Rust) - Port 8000
```bash
# Navigate to gateway service
cd app/gateway-service

# Build and run
cargo run

# Build release version
cargo build --release

# Check code formatting
cargo fmt --check

# Format code
cargo fmt

# Run with hot reloading (install cargo-watch first)
cargo install cargo-watch
cargo watch -x run

# Fix Rust version compatibility issues
# If encountering build errors about Rust version requirements:
# 1. Update Dockerfile to use newer Rust version:
#    Change "FROM rust:1.81 as builder" to "FROM rust:1.83 as builder"
# 2. Or update dependencies to compatible versions:
#    cargo update time-macros --precise 0.2.24
#    cargo update tinystr --precise 0.8.1
```

## Service Communication Patterns

### Authentication Flow
1. **Client** → **Gateway** (`/api/auth/login`) with credentials
2. **Gateway** forwards to **User Service**
3. **User Service** validates and returns JWT token
4. **Gateway** adds user context and forwards response
5. **Client** stores token and includes in `Authorization: Bearer {token}` header
6. Subsequent requests to gateway automatically validate tokens

### Real-time Chat Flow
1. **Client** connects WebSocket to **Gateway** (`ws://localhost:8000/api/chat/ws/{room_id}`)
2. **Gateway** validates JWT token and establishes connection
3. **Gateway** proxies WebSocket connection to **Chat Service**
4. **Chat Service** manages room membership and broadcasts messages
5. Messages are simultaneously persisted via **Message Service**

### Message Persistence Flow
1. **Chat Service** receives messages via WebSocket
2. **Chat Service** sends message data to **Message Service** via HTTP POST
3. **Message Service** stores in PostgreSQL with proper indexing
4. **Message Service** returns confirmation to **Chat Service**
5. **Chat Service** broadcasts stored message to all connected clients

### Cross-Service Data Consistency
- **User Service** is the source of truth for user identities
- **Chat Service** maintains real-time state in memory with periodic snapshots
- **Message Service** provides durable message storage
- **Gateway** acts as central coordinator for distributed transactions

## Database Schemas

### MongoDB (User Service)
```javascript
// Users collection
{
  _id: ObjectId,
  email: string,
  username: string,
  password_hash: string,
  created_at: Date,
  updated_at: Date,
  email_verified: boolean,
  profile: {
    display_name: string,
    avatar_url: string,
    bio: string
  }
}
```

### PostgreSQL (Message Service)
```sql
-- Messages table
CREATE TABLE messages (
  id UUID PRIMARY KEY,
  room_id VARCHAR(50),
  user_id INTEGER,
  username VARCHAR(100),
  content TEXT,
  message_type VARCHAR(20) DEFAULT 'text',
  parent_id UUID REFERENCES messages(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted BOOLEAN DEFAULT FALSE
);

-- Rooms table
CREATE TABLE rooms (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100),
  description TEXT,
  creator_id INTEGER,
  is_private BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Read receipts table
CREATE TABLE read_receipts (
  user_id INTEGER,
  message_id UUID,
  room_id VARCHAR(50),
  read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, message_id)
);
```

## Development Workflows

### Multi-Service Development
When working across multiple services, use these patterns:

**Local Development Setup:**
1. Start dependencies in Docker: `docker-compose up -d mongo postgres`
2. Develop one service locally while others run in containers
3. Use environment variables to point to Docker services

**Service Interaction Testing:**
```bash
# Test gateway routing
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"password123"}'

# Test direct service access (for debugging)
curl http://localhost:3001/api/users
```

### Debugging Strategies

**Cross-Service Issues:**
1. Check gateway logs for routing errors: `docker-compose logs gateway-service`
2. Verify service health: `curl http://localhost:8000/health`
3. Test individual services directly when needed

**Database Debugging:**
```bash
# Check MongoDB data
docker-compose exec mongo mongosh chatapp-users --eval "db.users.find()"

# Check PostgreSQL data  
docker-compose exec postgres psql -U postgres -d chatapp_messages -c "SELECT * FROM messages LIMIT 10;"
```

### Development Best Practices

### Code Organization Guidelines

**Service Boundaries:**
- Each service should have a single responsibility
- Services communicate only through well-defined APIs
- Shared code should be minimized - prefer duplication over tight coupling
- Database schemas are owned by individual services

**API Design Principles:**
- RESTful APIs for HTTP endpoints
- WebSocket for real-time communication
- Consistent error handling and response formats
- Proper HTTP status codes and meaningful error messages

### Development Workflow Recommendations

**Feature Development Process:**
1. Create feature branch from `dev`: `git checkout -b feature/new-feature`
2. Develop and test locally using Docker Compose
3. Run full test suite: `poetry run python run_tests_optimized.py full`
4. Create pull request to `dev` branch
5. Wait for CI pipeline completion
6. Merge after approval

**Hot Reloading Setup:**
```bash
# For Python services with auto-reload
cd app/chat-service
poetry run uvicorn chat_app.app:app --host 0.0.0.0 --port 3002 --reload

# For Node.js services with nodemon
cd app/user-service
npx nodemon server.js

# For Go services with air (install air first)
cd app/message-service
air

# For Rust services with cargo-watch
cd app/gateway-service
cargo watch -x run
```

### Testing Strategies

**Test Pyramid Implementation:**
- **Unit Tests**: Test individual functions and classes in isolation
- **Integration Tests**: Test service interactions through the gateway
- **End-to-End Tests**: Test complete user workflows (manual or automated)

**Mocking Best Practices:**
- Mock external HTTP calls in unit tests
- Use in-memory databases for integration tests when possible
- Mock time-dependent functions for consistent test results
- Avoid mocking internal service dependencies unnecessarily

### Performance Optimization Tips

**Caching Strategies:**
- Redis caching for frequently accessed data
- HTTP caching headers for static assets
- Database query result caching
- Connection pooling for database connections

**Database Optimization:**
- Proper indexing on frequently queried fields
- Connection pooling configuration
- Query optimization and EXPLAIN analysis
- Regular database maintenance tasks

### Security Considerations

**Authentication Security:**
- JWT token expiration and refresh mechanisms
- Secure password hashing (bcrypt/scrypt)
- Rate limiting on authentication endpoints
- Input validation and sanitization

**Data Protection:**
- Environment variable management for secrets
- TLS/SSL encryption for all service communications
- Regular security scanning in CI pipeline
- Dependency vulnerability monitoring

## Prerequisites

Before working with this codebase, ensure you have the following installed:

- **Docker and Docker Compose** - For containerized service deployment
- **Node.js 16+** - For user-service development
- **Python 3.8+** - For chat-service development  
- **Go 1.19+** - For message-service development
- **Rust/Cargo** - For gateway-service development
- **Poetry** - Python dependency management (`pip install poetry`)
- **Git** - Version control

### Optional Development Tools

```bash
# HTTP client for API testing
pip install httpie

# Database GUI tools
brew install --cask mongodb-compass pgadmin4

# Container management utilities
brew install docker-compose-switch

# System monitoring tools
brew install htop
```

### API Testing Tools
```bash
# Install httpie for better API testing
pip install httpie

# Test API endpoints with httpie
http POST :8000/api/auth/login email=test@example.com password=password123

# With JWT token
http GET :8000/api/users/profile Authorization:"Bearer $TOKEN"
```

### Database Management Tools
```bash
# MongoDB GUI tool
brew install mongodb-compass

# PostgreSQL GUI tool
brew install pgadmin4

# Redis CLI tools
brew install redis
redis-cli -h localhost -p 6379
```

### Container Management
```bash
# Docker Compose extensions
brew install docker-compose-switch

# Container monitoring
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# Container resource limits
docker-compose up -d --scale chat-service=3
```

### Debugging Tools
```bash
# Network debugging
tcpdump -i any port 3002

# Process monitoring
htop
lsof -i :3002

# Memory profiling (Python)
pip install memory_profiler
python -m memory_profiler script.py
```

### Local Development Without Docker
For working on individual services locally while keeping others in Docker:

1. **Stop the service you want to develop locally:**
   ```bash
   docker-compose stop user-service
   ```

2. **Navigate to service directory and start locally:**
   ```bash
   cd app/user-service
   npm install
   npm run dev
   ```

3. **Other services remain running in Docker:**
   ```bash
   docker-compose start  # starts remaining services
   ```

### Environment Variables
Each service expects specific environment variables:

**User Service (.env):**
```
PORT=3001
MONGODB_URI=mongodb://localhost:27017/chatapp-users
JWT_SECRET=your-jwt-secret
SMTP_HOST=smtp.example.com
SMTP_PORT=587
```

**Chat Service (.env):**
```
PORT=3002
REDIS_URL=redis://localhost:6379
```

**Message Service (.env):**
```
PORT=3003
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=chatapp_messages
DB_PORT=5432
```

**Gateway Service (.env):**
```
PORT=8000
USER_SERVICE_URL=http://localhost:3001
CHAT_SERVICE_URL=http://localhost:3002
MESSAGE_SERVICE_URL=http://localhost:3003
JWT_SECRET=super-secret-gateway-key
```

## Repository Structure

```
.
├── app/
│   ├── docker-compose.yml          # Main orchestration file for all services
│   ├── frontend-service/           # React/Vite SPA (Port 3000)
│   │   ├── src/                   # Source code
│   │   ├── public/                # Static assets
│   │   ├── package.json           # Dependencies and scripts
│   │   └── vite.config.js         # Vite configuration
│   ├── gateway-service/            # Rust API gateway/load balancer (Port 8000)
│   │   ├── src/                   # Rust source code
│   │   ├── Cargo.toml             # Rust dependencies
│   │   └── Dockerfile             # Docker configuration
│   ├── user-service/               # Node.js user management (Port 3001) [MongoDB]
│   │   ├── server.js              # Express server entry point
│   │   ├── routes/                # API route handlers
│   │   ├── models/                # Database models
│   │   ├── middleware/            # Custom middleware
│   │   ├── package.json           # Dependencies and scripts
│   │   └── .env                   # Environment variables
│   ├── chat-service/               # Python real-time chat (Port 3002)
│   │   ├── chat_app/              # Application code
│   │   │   ├── __init__.py        # Package initialization
│   │   │   ├── app.py             # FastAPI application setup
│   │   │   ├── models.py          # Pydantic data models
│   │   │   ├── services.py        # Business logic layer
│   │   │   ├── routes.py          # API endpoints
│   │   │   └── websocket.py       # WebSocket handlers
│   │   ├── tests/                 # Test suite
│   │   │   ├── unit/              # Unit tests
│   │   │   ├── integration/       # Integration tests
│   │   │   ├── security/          # Security tests
│   │   │   └── linting/           # Linting tests
│   │   ├── scripts/               # Test runners
│   │   │   ├── run_tests.py       # Traditional runner
│   │   │   └── run_tests_optimized.py  # Fast runner
│   │   ├── pyproject.toml         # Poetry configuration
│   │   └── requirements.txt       # Python dependencies
│   └── message-service/            # Go message persistence (Port 3003) [PostgreSQL]
│       ├── main.go                # Go application entry point
│       ├── handlers/              # HTTP handlers
│       ├── models/                # Data models
│       ├── database/              # Database connection logic
│       ├── go.mod                 # Go modules
│       └── Dockerfile             # Docker configuration
├── .github/
│   └── workflows/
│       └── ci.yml                  # CI/CD pipeline configuration
├── AGENTS.md                       # This file - Development guide and architecture documentation
└── README.md                       # Project overview and quick start guide
```

## Advanced Testing Commands

### Running Specific Tests

**Chat Service - Targeted Testing:**
```bash
# Run only API tests
poetry run pytest tests/unit/test_api.py -v

# Run only model tests
poetry run pytest tests/unit/test_models.py -v

# Run only service tests
poetry run pytest tests/unit/test_services.py -v

# Run integration tests
poetry run pytest tests/integration/ -v

# Run with specific markers
poetry run pytest -m "not slow"  # Skip slow tests
poetry run pytest -m "security"  # Run only security tests
```

**Debugging Test Failures:**
```bash
# Run tests with verbose output and stop on first failure
poetry run pytest -xvs

# Run tests with coverage report
poetry run pytest --cov=chat_app --cov-report=html tests/

# Run tests and generate coverage badge
poetry run pytest --cov=chat_app --cov-report=term-missing tests/
```

### Test Environment Setup

**Setting up test databases:**
```bash
# For integration tests requiring databases
docker-compose up -d mongo postgres redis

# Run tests with external services
poetry run pytest tests/integration/ -v

# Clean up test containers
docker-compose down
```

### Performance Testing

**Load Testing Commands:**
```bash
# Install load testing tools
pip install locust

# Run load tests (from chat-service directory)
locust -f tests/performance/load_test.py --headless -u 100 -r 10

# WebSocket load testing
# Use artillery or similar tools for WebSocket performance testing
```

## Monitoring and Debugging

### Service Health Checks
```bash
# Check individual service health
curl http://localhost:8000/health          # Gateway + all services
curl http://localhost:3001/                # User service
curl http://localhost:3002/health          # Chat service  
curl http://localhost:3003/health          # Message service

# Check database connectivity
docker-compose exec mongo mongosh --eval "db.stats()"
docker-compose exec postgres psql -U postgres -c "SELECT COUNT(*) FROM messages;"
```

### Log Analysis
```bash
# View all service logs
docker-compose logs -f

# View specific service logs with context
docker-compose logs -f --tail=100 user-service
docker-compose logs -f --since=1h gateway-service

# Search logs for specific patterns
docker-compose logs | grep "ERROR"
docker-compose logs | grep "WebSocket"
```

### Performance Monitoring
- **Gateway Service:** Tracks request latency, error rates, and throughput
- **Database Connections:** Monitor pool utilization and query performance
- **WebSocket Connections:** Track active connections and message throughput
- **Memory Usage:** Monitor service memory consumption, especially Chat Service

### Production Deployment Considerations

**Environment Configuration:**
- Use proper environment variables for production secrets
- Configure appropriate JWT token expiration times
- Set up monitoring and alerting for service health
- Implement proper logging aggregation and retention policies

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
- Database connection pooling and timeouts

**Monitoring and Observability:**
- Gateway service tracks request latency and error rates
- Health checks available at `/health` endpoint for each service
- Structured logging for log aggregation systems
- Consider implementing distributed tracing for cross-service requests

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

**Service Discovery Issues:**
- Verify Docker network connectivity
- Check service URLs in gateway configuration
- Confirm container port mappings

**Docker Build Issues (Rust):**
- If encountering Rust version compatibility errors, update the Dockerfile base image to a newer Rust version (1.83+)
- Alternatively, pin problematic dependencies to older versions that support the current Rust version

## CI/CD Pipeline

The repository uses GitHub Actions for continuous integration with automated testing, security scanning, and Docker image building:

### Pipeline Stages

1. **Frontend Testing Stage** - Runs on every push/PR to `main` and `dev` branches:
   - Node.js setup with caching
   - Frontend dependency installation
   - Unit tests execution
   - ESLint linting
   - Production build verification

2. **Backend Testing Stage** - Runs on every push/PR to `main` and `dev` branches:
   - Matrix strategy for different services
   - Python setup with Poetry dependency management
   - Comprehensive caching for faster builds
   - Unit tests with optimized runner (`run_tests_optimized.py fast`)
   - Security scanning with Safety and Bandit
   - Code quality checks with Flake8, Black, and MyPy

3. **Docker Build & Push Stage** - Runs only on pushes to `main` branch:
   - Multi-architecture builds (linux/amd64, linux/arm64)
   - Builds Docker images for all services
   - Pushes to GitHub Container Registry (GHCR)
   - Comprehensive build caching for performance

### CI Caching Strategy

The pipeline implements extensive caching to optimize build times:

**Language-Specific Caching:**
- **Node.js**: `~/.npm` and `node_modules` caching
- **Python**: Poetry virtual environments and pip cache
- **Go**: Module cache and sum files
- **Rust**: Cargo registry, git dependencies, and target directory
- **Docker**: Buildx cache for layer reuse

**Performance Improvements:**
- Poetry dependency caching reduces Python builds from 2-3 minutes to 30-60 seconds
- Node.js module caching cuts frontend builds from 1-2 minutes to 20-40 seconds
- Rust compilation caching provides 95%+ improvement (30+ minutes → 1-2 minutes)
- Docker layer caching enables incremental builds

### Security Scanning in CI

Automated security checks include:
```bash
# Dependency vulnerability scanning
poetry run safety check

# Static code analysis
poetry run bandit -r chat_app/ -ll

# The pipeline runs these automatically and reports findings
```

### Code Quality Enforcement

The CI pipeline enforces code quality standards:
- **Flake8 linting** with customized ignore rules
- **Black formatting** compliance checking
- **MyPy type checking** for Python services
- **ESLint** for frontend JavaScript/TypeScript code

### Security Checks in CI

The pipeline automatically runs these security validations:

```yaml
# Dependency security scanning
poetry run safety check

# Static code analysis for security issues
poetry run bandit -r chat_app/ -ll

# Custom AST-based security scanning
# Detects eval(), exec(), and other dangerous patterns
```

### Code Quality Checks in CI

```yaml
# Linting with flake8
poetry run flake8 chat_app/ --max-line-length=100

# Code formatting with black
poetry run black --check chat_app/

# Type checking with mypy
poetry run mypy chat_app/
```

### Local Pipeline Testing

To test the CI pipeline locally:

```bash
# Navigate to chat service
cd app/chat-service

# Install additional CI tools
poetry add --group dev bandit safety

# Run the same checks as CI
poetry run safety check
poetry run bandit -r chat_app/ -ll
poetry run flake8 chat_app/
poetry run black --check chat_app/
poetry run mypy chat_app/
```

### Pipeline Configuration

The workflow is defined in `.github/workflows/ci.yml` and includes:
- Matrix strategy for testing different services
- Automatic dependency installation
- Comprehensive security scanning
- Code quality enforcement
- Docker image building and publishing

### Testing Strategies

**Unit Testing Approach:**
- Each service has isolated unit tests in their respective `tests/unit/` directories
- Use the optimized test runner for faster feedback: `poetry run python run_tests_optimized.py fast`
- Mock external dependencies (database calls, HTTP requests) in unit tests

**Integration Testing:**
- Test service interactions through the gateway
- Use Docker Compose to spin up all services for end-to-end testing
- Focus on authentication flows and data consistency between services

**Test Commands Summary:**
```bash
# Fast unit tests (recommended for development)
poetry run python run_tests_optimized.py fast

# Full test suite with coverage
poetry run python run_tests_optimized.py coverage

# Specific test categories
poetry run python run_tests_optimized.py security  # Security scanning
poetry run python run_tests_optimized.py lint      # Code quality
poetry run python run_tests_optimized.py type-check # Type checking

# Run individual test files
poetry run pytest tests/unit/test_api.py -v
poetry run pytest tests/integration/ -v
```

## Error Handling and Logging

**Logging Patterns:**
- Gateway service uses structured logging with log levels
- Services log important events, errors, and performance metrics
- Use consistent log formats across services for easier debugging

**Error Response Format:**
```json
{
  "error": "Descriptive error message",
  "details": "Additional context",
  "timestamp": "ISO 8601 timestamp"
}
```

**Common Error Types:**
- `400 Bad Request`: Invalid input or validation errors
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: Valid token but insufficient permissions
- `404 Not Found`: Resource doesn't exist
- `500 Internal Server Error`: Service failures
- `503 Service Unavailable`: Downstream service issues

## Troubleshooting Guide

### Service Startup Issues

**Check Service Status:**
```bash
# View all container status
docker-compose ps

# Check specific service logs
docker-compose logs user-service
docker-compose logs chat-service
docker-compose logs message-service
docker-compose logs gateway-service
```

**Restart Individual Services:**
```bash
# Restart specific service
docker-compose restart user-service

# Rebuild and restart
docker-compose build --no-cache user-service
docker-compose up -d user-service
```

### Database Connection Issues

**MongoDB Troubleshooting:**
```bash
# Check MongoDB connection
docker-compose exec mongo mongosh --eval "db.stats()"

# View MongoDB logs
docker-compose logs mongo

# Connect to MongoDB shell
docker-compose exec mongo mongosh chatapp-users

# Check users collection
db.users.find().pretty()
```

**PostgreSQL Troubleshooting:**
```bash
# Check PostgreSQL connection
docker-compose exec postgres psql -U postgres -c "SELECT version();"

# View PostgreSQL logs
docker-compose logs postgres

# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d chatapp_messages

# Check messages table
SELECT COUNT(*) FROM messages;
SELECT * FROM messages ORDER BY created_at DESC LIMIT 10;
```

### Authentication Issues

**JWT Token Debugging:**
```bash
# Test user registration
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Test user login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Test protected endpoint with token
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/api/users/profile
```

### WebSocket Connection Issues

**WebSocket Debugging:**
```bash
# Test WebSocket connection
websocat ws://localhost:8000/api/chat/ws/room1

# Or use wscat
npm install -g wscat
wscat -c ws://localhost:8000/api/chat/ws/room1

# Check CORS configuration
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Authorization" \
     -X OPTIONS http://localhost:8000/api/chat/ws/room1
```

### Performance Monitoring

**Resource Usage Monitoring:**
```bash
# Monitor container resource usage
docker stats

# Monitor specific service CPU/Memory
docker stats user-service chat-service message-service gateway-service

# Check Docker disk usage
docker system df
```

**Network Troubleshooting:**
```bash
# Check Docker network connectivity
docker network ls
docker network inspect app_default

# Test service connectivity
docker-compose exec gateway-service curl -v http://user-service:3001/health
docker-compose exec gateway-service curl -v http://chat-service:3002/health
docker-compose exec gateway-service curl -v http://message-service:3003/health
```

### Common Fixes

**Rust Build Issues:**
```bash
cd app/gateway-service

# Option 1: Update Dockerfile to use newer Rust version
sed -i 's/rust:1.81/rust:1.83/' Dockerfile

# Option 2: Update specific dependencies to compatible versions
cargo update time-macros --precise 0.2.24
cargo update tinystr --precise 0.8.1

# Clean and rebuild
cargo clean
cargo build
```

**Python Dependency Issues:**
```bash
cd app/chat-service

# Update Poetry lock file
poetry lock --no-update

# Clear Poetry cache
poetry cache clear pypi --all

# Reinstall dependencies
poetry install
```

**Node.js Issues:**
```bash
cd app/user-service

# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Docker Cleanup:**
```bash
# Remove unused containers, networks, and images
docker system prune -a

# Remove volumes
docker volume prune

# Reset everything (use with caution)
docker-compose down -v --remove-orphans
docker-compose up -d
```