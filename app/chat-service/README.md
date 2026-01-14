# Chat Service Microservice

A real-time chat microservice built with Python, FastAPI, and WebSocket technology. This service provides advanced chat functionality including real-time messaging, user presence tracking, typing indicators, message reactions, and threaded conversations.

## Features

- 🟢 **Real-time Messaging**: WebSocket-based instant messaging
- 👥 **User Presence Tracking**: Live online/offline status indicators
- ⌨️ **Typing Indicators**: Real-time typing notifications
- 😄 **Message Reactions**: Emoji reactions to messages
- 🔧 **Threaded Conversations**: Reply to specific messages
- 🔒 **Private Rooms**: Support for private chat rooms
- 🏠 **Room Management**: Create, join, and leave chat rooms
- 📱 **RESTful API**: Standard HTTP endpoints for chat operations

## Technology Stack

- **Framework**: FastAPI
- **WebSocket**: Built-in WebSocket support
- **Data Validation**: Pydantic models
- **ASGI Server**: Uvicorn
- **Testing**: Pytest with async support

## Project Structure

```
chat-service/
├── chat_app/                   # Main application package
│   ├── __init__.py            # Package initialization
│   ├── app.py                 # FastAPI application setup
│   ├── models.py              # Pydantic data models
│   ├── services.py            # Business logic layer
│   ├── routes.py              # API endpoints
│   └── websocket.py           # WebSocket handlers
├── tests/                     # Test suite
│   ├── conftest.py           # Test configuration
│   ├── test_api.py           # API endpoint tests
│   ├── test_models.py        # Model validation tests
│   └── test_services.py      # Business logic tests
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Poetry configuration
├── run_tests.py              # Test runner script
└── README.md                 # This file
```

## Prerequisites

- Python 3.8+
- pip or Poetry for dependency management

## Installation

### Using pip:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Using Poetry (recommended):

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate the Poetry shell
poetry shell
```

## Running the Service

### Development Mode

```bash
# Using pip/venv
python main.py

# Using Poetry
poetry run python main.py

# With auto-reload for development
uvicorn chat_app.app:app --reload --host 0.0.0.0 --port 3002
```

### Production Mode

```bash
# Using pip/venv
uvicorn chat_app.app:app --host 0.0.0.0 --port 3002 --workers 4

# Using Poetry
poetry run uvicorn chat_app.app:app --host 0.0.0.0 --port 3002 --workers 4
```

The service will be available at: `http://localhost:3002`

## API Documentation

Once the service is running, you can access:

- **Swagger UI**: `http://localhost:3002/docs`
- **ReDoc**: `http://localhost:3002/redoc`
- **OpenAPI JSON**: `http://localhost:3002/openapi.json`

## API Endpoints

### Health Check
```
GET /
```

### Room Management
```
POST /api/rooms              # Create a new room
GET /api/rooms               # List all rooms
GET /api/rooms/{room_id}     # Get room details
```

### Room Participation
```
POST /api/rooms/{room_id}/join   # Join a room
POST /api/rooms/{room_id}/leave  # Leave a room
```

### Messaging
```
POST /api/messages                    # Send a message
GET /api/rooms/{room_id}/messages     # Get room messages
```

### Real-time Features
```
POST /api/typing     # Update typing status
POST /api/reactions  # Add message reactions
```

### WebSocket Endpoint
```
WebSocket /ws/{room_id}/{user_id}
```

## WebSocket Communication

The WebSocket endpoint supports real-time communication with the following message types:

### Client to Server Messages

```json
{
  "type": "ping"
}
```

```json
{
  "type": "typing",
  "username": "john_doe",
  "is_typing": true
}
```

### Server to Client Messages

```json
{
  "type": "message",
  "message": {
    "id": "uuid",
    "room_id": "room-uuid",
    "user_id": 123,
    "username": "john_doe",
    "content": "Hello world!",
    "timestamp": "2023-01-01T12:00:00Z"
  }
}
```

```json
{
  "type": "typing_update",
  "room_id": "room-uuid",
  "typing_users": ["123", "456"],
  "timestamp": "2023-01-01T12:00:00Z"
}
```

```json
{
  "type": "user_joined",
  "user_id": 123,
  "username": "john_doe",
  "room_id": "room-uuid",
  "timestamp": "2023-01-01T12:00:00Z"
}
```

## Data Models

### CreateRoomRequest
```json
{
  "name": "General Chat",
  "creator_id": 123,
  "description": "A general discussion room",
  "is_private": false,
  "invited_users": [456, 789]
}
```

### MessageRequest
```json
{
  "room_id": "room-uuid",
  "user_id": 123,
  "username": "john_doe",
  "content": "Hello everyone!",
  "message_type": "text",
  "parent_id": "optional-reply-id"
}
```

### TypingRequest
```json
{
  "room_id": "room-uuid",
  "user_id": 123,
  "username": "john_doe",
  "is_typing": true
}
```

## Running Tests

### Run All Tests
```bash
# Using the test runner script
python run_tests.py

# Using pytest directly
pytest

# Using Poetry
poetry run pytest
```

### Run Specific Test Categories
```bash
# Run only API tests
pytest tests/test_api.py

# Run only model tests
pytest tests/test_models.py

# Run only service tests
pytest tests/test_services.py
```

### Run Tests with Coverage
```bash
# Generate coverage report
pytest --cov=chat_app --cov-report=html

# Run with verbose output
pytest -v

# Run with coverage and verbose output
pytest --cov=chat_app -v
```

### Test Options
```bash
# Run tests in parallel
pytest -n auto

# Run only failed tests
pytest --lf

# Run tests matching pattern
pytest -k "test_create_room"
```

## Environment Variables

Create a `.env` file in the project root:

```env
# Server configuration
HOST=0.0.0.0
PORT=3002

# Logging
LOG_LEVEL=info

# Optional: Database connection (for future enhancements)
# DATABASE_URL=postgresql://user:password@localhost:5432/chat_db
```

## Docker Support

### Build Docker Image
```bash
docker build -t chat-service .
```

### Run with Docker
```bash
docker run -p 3002:3002 chat-service
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  chat-service:
    build: .
    ports:
      - "3002:3002"
    environment:
      - PORT=3002
```

## Development Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes

### Testing
- Write unit tests for all business logic
- Aim for >90% test coverage
- Use pytest fixtures for test setup
- Test both success and failure cases

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push and create PR
git push origin feature/new-feature
```

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Kill process using port 3002
   lsof -ti:3002 | xargs kill -9
   ```

2. **Import errors**:
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

3. **WebSocket connection issues**:
   - Check CORS settings
   - Verify room exists before connecting
   - Ensure proper authentication headers

### Logging

Enable debug logging:
```bash
export LOG_LEVEL=debug
python main.py
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License

This project is licensed under the MIT License.

## Contact

For questions or support, please open an issue on the GitHub repository.