# GitHub Actions CI/CD Documentation

This repository uses GitHub Actions for Continuous Integration and Continuous Deployment.

## Workflows Overview

### 1. CI Pipeline (`ci.yml`)
**Trigger:** Push to `main`/`develop` branches, Pull Requests
**Purpose:** Automated testing and validation

**Jobs:**
- `build-and-test`: Builds each service using Docker
- `test-services`: Runs integration tests using docker-compose
- `code-quality`: Performs security scans and configuration validation
- `dependency-analysis`: Checks for vulnerable dependencies
- `notification`: Sends pipeline status notifications

### 2. Deploy to Production (`deploy.yml`)
**Trigger:** Push to `main` branch, Manual trigger
**Purpose:** Production deployment

**Jobs:**
- `build-and-push`: Builds and pushes Docker images to registry
- `deploy`: Deploys services to production environment

### 3. Code Scanning (`security.yml`)
**Trigger:** Push/Pull Request, Weekly scheduled scans
**Purpose:** Security vulnerability detection

**Jobs:**
- `codeql-analysis`: Static code analysis for multiple languages
- `security-scanning`: Container and filesystem vulnerability scanning
- `secret-detection`: Detection of hardcoded secrets

## Setup Requirements

### Secrets Needed:
- `DOCKER_USERNAME`: Docker Hub/GCR username
- `DOCKER_PASSWORD`: Docker registry password/token

### Environment Variables:
- Configure in GitHub repository settings under "Environments"

## Local Testing

To test workflows locally:

```bash
# Validate docker-compose configuration
cd app && docker compose config

# Run tests manually
docker compose up -d
docker compose exec user-service ./full_test.sh
```

## Monitoring

- Check workflow runs in GitHub Actions tab
- View security alerts in Security tab
- Monitor deployment status in deployment environments