# CI/CD Status Badges

## Test Status
![Unit Tests](https://github.com/your-username/your-repo/actions/workflows/unit-tests.yml/badge.svg)
![CI/CD Pipeline](https://github.com/your-username/your-repo/actions/workflows/ci.yml/badge.svg)

## Microservice Status
![User Service Tests](https://github.com/your-username/your-repo/actions/workflows/unit-tests.yml/badge.svg?job=user-service)
![Chat Service Tests](https://github.com/your-username/your-repo/actions/workflows/unit-tests.yml/badge.svg?job=chat-service)
![Message Service Tests](https://github.com/your-username/your-repo/actions/workflows/unit-tests.yml/badge.svg?job=message-service)
![Gateway Service Tests](https://github.com/your-username/your-repo/actions/workflows/unit-tests.yml/badge.svg?job=gateway-service)

---

## CI Configuration Files

This repository includes automated CI/CD workflows for testing and building microservices:

### Workflows

1. **`.github/workflows/unit-tests.yml`** - Runs unit tests for all microservices
2. **`.github/workflows/ci.yml`** - Main CI/CD pipeline (includes unit tests + Docker builds)

### Test Matrix

The CI runs tests for each service with appropriate language environments:

- **User Service**: Node.js 18 with Jest
- **Chat Service**: Python 3.11 
- **Message Service**: Go 1.21
- **Gateway Service**: Python 3.11

### Manual Trigger

You can manually trigger tests using:
```bash
gh workflow run unit-tests.yml
```

### Test Results

Test results are uploaded as artifacts and can be viewed in the GitHub Actions summary.