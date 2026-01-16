# AGENTS.md

This file provides guidance to Qoder (qoder.com) when working with code in this microservices repository.

## Development Commands

### Docker Orchestration
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View service logs
docker-compose logs -f [service-name]

# Rebuild specific service
docker-compose build [service-name]

# Restart specific service
docker-compose restart [service-name]
```

### Service-Specific Development
Each service can be developed independently:

#### User Service (Node.js)
```bash
cd user-service
npm install
npm run dev
# Runs on port 3001
```

#### Chat Service (Python)
```bash
cd chat-service
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 3002
# Runs on port 3002
```

#### Message Service (Go)
```bash
cd message-service
go mod tidy
go run main.go
# Runs on port 3003
```

#### Gateway Service (Python/Flask)
```bash
cd gateway-service
pip install -r requirements.txt
python app.py
# Runs on port 8000
```

#### Frontend Service (React)
```bash
cd frontend-service
npm install
npm run dev
# Runs on port 3000
```

## Project Architecture Overview

### Microservices Structure
```
app/
├── user-service/       # Node.js + Express + MongoDB (Port 3001)
├── chat-service/       # Python + FastAPI + WebSocket (Port 3002)
├── message-service/    # Go + Gin + PostgreSQL (Port 3003)
├── gateway-service/    # Python + Flask API Gateway (Port 8000)
├── frontend-service/   # React + Vite (Port 3000)
└── docker-compose.yml  # Service orchestration
```

### Key Architectural Patterns
- **Polyglot Persistence**: Each service uses its optimal database (MongoDB, PostgreSQL)
- **API Gateway Pattern**: Centralized routing and service aggregation through gateway-service
- **Service Isolation**: Independent deployment and scaling of each microservice
- **Cross-Service Communication**: HTTP REST APIs and WebSocket connections
- **Database per Service**: Each service owns its data store

### Service Responsibilities
- **User Service**: Authentication, user management, JWT token generation
- **Chat Service**: Real-time chat rooms, presence tracking, WebSocket connections
- **Message Service**: Message storage, retrieval, PostgreSQL persistence
- **Gateway Service**: API routing, request aggregation, CORS handling
- **Frontend Service**: React UI, service monitoring, user interface

### Data Flow Patterns
1. **Authentication Flow**: Frontend → Gateway → User Service
2. **Chat Creation**: Frontend → Gateway → Chat Service
3. **Message Sending**: Frontend → Gateway → Message Service
4. **Real-time Updates**: Chat Service ↔ Frontend (WebSocket)

## Environment Variables
Each service requires specific environment variables defined in docker-compose.yml:
- Database connection strings
- JWT secret keys
- Service ports and hostnames
- CORS origins

## Common Development Tasks
- Test service connectivity using docker-compose logs
- Validate API endpoints through gateway service
- Monitor service health via frontend dashboard
- Debug cross-service communication issues
- Update docker-compose when adding new services

## Testing Strategy
- Individual service testing using their native test frameworks
- Integration testing through docker-compose setup
- End-to-end testing via frontend service interactions
- WebSocket connection testing for real-time features

## Deployment Considerations
- Services communicate through docker network
- Database services (mongo, postgres) are separate containers
- Gateway service acts as single entry point
- Frontend connects to gateway for all API calls