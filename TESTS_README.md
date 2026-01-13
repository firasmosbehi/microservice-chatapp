# Microservices Test Suite

This directory contains organized unit tests for all microservices in the chat application.

## Test Structure

Each service has its own `tests/` directory containing:

- **Unit tests** for individual components and functions
- **Integration tests** for API endpoints and workflows  
- **Test runners** with proper setup, teardown, and reporting
- **Helper utilities** for test setup and mocking

## Running Tests

### Run All Services Tests

```bash
# Sequential execution (recommended for CI)
python run_microservice_tests.py

# Parallel execution (faster for local development)
python run_microservice_tests.py --parallel
```

### Run Individual Service Tests

#### User Service (Node.js)
```bash
cd app/user-service
node tests/run-tests.js
```

#### Chat Service (Python)
```bash
cd app/chat-service
python tests/run_tests.py
```

#### Message Service (Go)
```bash
cd app/message-service
./tests/run_tests.sh
```

#### Gateway Service (Python/Rust)
```bash
cd app/gateway-service
python tests/run_tests.py
```

## Test Organization

```
app/
├── user-service/
│   └── tests/
│       ├── user-api.test.js          # API endpoint tests
│       ├── user-utils.test.js        # Utility function tests
│       ├── integration.test.js       # Integration tests
│       └── run-tests.js              # Test runner
│
├── chat-service/
│   └── tests/
│       ├── test_api_endpoints.py     # FastAPI endpoint tests
│       ├── test_models.py            # Pydantic model tests
│       ├── test_websocket.py         # WebSocket tests
│       ├── simple_test.py            # Basic functionality tests
│       ├── advanced_test.py          # Advanced scenario tests
│       └── run_tests.py              # Test runner
│
├── message-service/
│   └── tests/
│       ├── handlers_test.go          # HTTP handler tests
│       ├── models_test.go            # Data model tests
│       ├── utils_test.go             # Utility function tests
│       ├── main_test.go              # Integration tests
│       └── run_tests.sh              # Test runner
│
└── gateway-service/
    └── tests/
        ├── test_app.py               # Flask app tests
        └── run_tests.py              # Test runner
```

## Features

### Master Test Runner
- ✅ Runs tests for all services in sequence or parallel
- ✅ Colored output for easy readability
- ✅ Detailed error reporting
- ✅ Execution time tracking
- ✅ Summary statistics

### Individual Service Runners
- ✅ Automatic dependency installation
- ✅ Environment setup and teardown
- ✅ Coverage reporting where applicable
- ✅ Proper error handling and timeouts

## Test Coverage

Each service includes tests for:

### User Service
- ✅ User registration and validation
- ✅ Authentication and JWT token management
- ✅ Profile management
- ✅ Password reset flows
- ✅ Email verification
- ✅ Utility functions (hashing, validation)

### Chat Service  
- ✅ Room creation and management
- ✅ User joining/leaving rooms
- ✅ Message sending and retrieval
- ✅ WebSocket connections
- ✅ Typing indicators
- ✅ Presence detection
- ✅ Model validation

### Message Service
- ✅ Message CRUD operations
- ✅ Database interactions
- ✅ Read receipt tracking
- ✅ Query optimization
- ✅ Error handling

### Gateway Service
- ✅ Request routing and proxying
- ✅ JWT token validation
- ✅ CORS handling
- ✅ Rate limiting
- ✅ Error responses

## Continuous Integration

The test suite is designed for CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Microservice Tests
  run: python run_microservice_tests.py
```

## Best Practices

- Tests are isolated and don't depend on external services
- Proper setup/teardown for database connections
- Mock external dependencies where appropriate
- Clear test naming conventions
- Comprehensive error case coverage
- Performance considerations for test execution

## Troubleshooting

### Common Issues

1. **Missing dependencies**: Runners automatically install required packages
2. **Database connection errors**: Tests use isolated test databases
3. **Port conflicts**: Services use random ports during testing
4. **Timeout issues**: Tests have reasonable timeout limits

### Debugging Tests

```bash
# Run with verbose output
python run_microservice_tests.py --verbose

# Run specific service tests
cd app/user-service && npm test -- --verbose
```

## Contributing

When adding new tests:

1. Place tests in the appropriate service's `tests/` directory
2. Follow the existing naming conventions
3. Include both positive and negative test cases
4. Update the master test runner if adding new services
5. Ensure tests run in isolation