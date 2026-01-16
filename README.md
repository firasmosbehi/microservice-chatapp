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
poetry run python run_tests_optimized.py fast

# Full test suite with coverage
poetry run python run_tests_optimized.py coverage

# Run specific test modes
poetry run python run_tests_optimized.py security  # Security scanning
poetry run python run_tests_optimized.py lint      # Code quality
poetry run python run_tests_optimized.py type-check # Type checking
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