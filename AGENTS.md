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

### Prerequisites
- Docker and Docker Compose
- Node.js 16+ (for user-service development)
- Python 3.8+ (for chat-service development)
- Go 1.19+ (for message-service development)
- Rust/Cargo (for gateway-service development)

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
app/
├── docker-compose.yml          # Main orchestration file
├── frontend-service/           # React/Vite SPA
├── gateway-service/            # Rust API gateway/load balancer
├── user-service/               # Node.js user management [MongoDB]
├── chat-service/               # Python real-time chat
└── message-service/            # Go message persistence [PostgreSQL]
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

### Error Handling and Logging

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

```bash
# Check service health
curl http://localhost:8000/health
curl http://localhost:3001/
curl http://localhost:3002/
curl http://localhost:3003/

# View docker container status
docker-compose ps

# Check database connections
docker-compose exec mongo mongosh
docker-compose exec postgres psql -U postgres

# Restart specific service
docker-compose restart user-service

# Rebuild specific service
docker-compose build --no-cache user-service

# Fix Rust build issues
cd app/gateway-service
# Option 1: Update Dockerfile to use newer Rust version
sed -i 's/rust:1.81/rust:1.83/' Dockerfile
# Option 2: Update specific dependencies to compatible versions
cargo update time-macros --precise 0.2.24
cargo update tinystr --precise 0.8.1
```