# ChatApp Microservices with Frontend

Multi-language microservices chat application with React frontend.

## Services
- Frontend Service (React) - Port 3000
- Gateway Service (Rust) - Port 8000
- User Service (Node.js) - Port 3001
- Chat Service (Python) - Port 3002  
- Message Service (Go) - Port 3003

## Quick Start
```bash
cd app
docker-compose up -d
```

## Access Points
- Frontend UI: http://localhost:3000
- Gateway API: http://localhost:8000
- Individual services on their respective ports

The frontend includes:
- Service status monitoring
- Simple chat interface
- API connectivity through gateway