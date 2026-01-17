# GitHub Issues Templates

This document contains pre-formatted issues for the microservice-chatapp repository. You can copy and paste these directly into GitHub's issue creation interface.

## 🐛 Bug Reports

### Issue 1: Frontend Service Caching Error in CI Pipeline
```
---
name: Frontend Service Caching Error in CI Pipeline
about: GitHub Actions setup-node fails to cache npm dependencies
title: '[BUG] Frontend service CI pipeline fails with npm caching error'
labels: bug, ci-cd, frontend
assignees: ''

---

## Bug Description
The GitHub Actions CI pipeline fails during the frontend service build step with the error:
"Some specified paths were not resolved, unable to cache dependencies"

## Steps to Reproduce
1. Push changes to main or dev branch
2. Trigger CI pipeline
3. Observe failure in frontend-test job

## Expected Behavior
The setup-node action should successfully cache npm dependencies and the pipeline should complete without errors.

## Actual Behavior
Pipeline fails with caching error, preventing frontend tests and build from completing.

## Environment
- Repository: firasmosbehi/microservice-chatapp
- Branch: main/dev
- GitHub Actions runner: ubuntu-latest

## Additional Context
This affects the frontend service specifically. The error occurs in the actions/setup-node@v3 step when trying to cache npm dependencies.

## Possible Solution
Remove explicit cache-dependency-path configuration and let setup-node use default behavior.
```

### Issue 2: Poetry Lock File Mismatch
```
---
name: Poetry Lock File Mismatch in Chat Service
about: Dependency resolution conflicts cause installation failures
title: '[BUG] Poetry install fails due to pyproject.toml and poetry.lock mismatch'
labels: bug, dependencies, python, chat-service
assignees: ''

---

## Bug Description
Poetry install command fails with error indicating significant changes between pyproject.toml and poetry.lock files.

## Steps to Reproduce
1. Navigate to app/chat-service directory
2. Run `poetry install`
3. Observe dependency resolution error

## Expected Behavior
Dependencies should install successfully based on the current pyproject.toml configuration.

## Actual Behavior
Error message: "pyproject.toml changed significantly since poetry.lock was last generated. Run `poetry lock` to fix the lock file."

## Environment
- Service: Chat Service (Python/FastAPI)
- Poetry version: Latest
- Python version: 3.8+

## Additional Context
This commonly occurs when dependencies are updated in pyproject.toml without regenerating the lock file.

## Solution
Run `poetry lock` followed by `poetry install` to synchronize the dependency files.
```

## ✨ Feature Requests

### Issue 3: Add User Profile Picture Upload
```
---
name: Add User Profile Picture Upload Feature
about: Enable users to upload and manage profile pictures
title: '[FEATURE] Implement user profile picture upload functionality'
labels: enhancement, user-service, frontend
assignees: ''

---

## Feature Description
Add capability for users to upload, update, and manage profile pictures in their accounts.

## Problem Statement
Currently users can only set text-based profile information. Adding profile pictures would enhance user experience and make the chat application more engaging.

## Proposed Solution
Implement profile picture upload with the following features:
- Image upload endpoint in User Service
- Image validation (size, format, dimensions)
- Cloud storage integration (AWS S3, Google Cloud Storage, or similar)
- Profile picture display in frontend chat interface
- Avatar fallback for users without profile pictures

## Technical Requirements
- REST API endpoint for image upload
- Image processing/validation middleware
- Database schema updates for storing image URLs
- Frontend components for image selection and preview
- Security measures to prevent malicious file uploads

## Acceptance Criteria
- [ ] Users can upload profile pictures through the UI
- [ ] Images are properly validated before storage
- [ ] Profile pictures display correctly in chat interfaces
- [ ] Fallback avatars are shown for users without pictures
- [ ] Image storage is secure and scalable
```

### Issue 4: Implement Message Search Functionality
```
---
name: Implement Message Search Across Rooms
about: Add full-text search capability for messages in all chat rooms
title: '[FEATURE] Add global message search functionality'
labels: enhancement, message-service, chat-service, frontend
assignees: ''

---

## Feature Description
Enable users to search through their message history across all chat rooms with full-text search capabilities.

## Problem Statement
Users currently cannot search through past messages, making it difficult to find specific conversations or information shared previously.

## Proposed Solution
Implement Elasticsearch or PostgreSQL full-text search integration with:
- Real-time indexing of new messages
- Search API endpoint with filtering options
- Frontend search interface with autocomplete
- Search result highlighting
- Filtering by date range, room, user

## Technical Requirements
- Message Service integration with search engine
- Indexing strategy for efficient searching
- Search API with pagination support
- Frontend search component with debouncing
- Performance optimization for large datasets

## Acceptance Criteria
- [ ] Users can search messages across all rooms they have access to
- [ ] Search results load quickly with proper pagination
- [ ] Search supports filtering by room, date, and user
- [ ] Search terms are highlighted in results
- [ ] Real-time indexing keeps search results up to date
```

## 🔧 Technical Debt

### Issue 5: Refactor Chat Service WebSocket Handler
```
---
name: Refactor Chat Service WebSocket Handler for Better Scalability
about: Current WebSocket implementation needs architectural improvements
title: '[TECH DEBT] Refactor WebSocket handler for improved scalability'
labels: tech-debt, chat-service, scalability
assignees: ''

---

## Technical Debt Description
The current WebSocket implementation in the Chat Service uses in-memory storage for connection state, which limits horizontal scaling capabilities.

## Current Issues
- In-memory state management prevents horizontal scaling
- No persistence for connection state across service restarts
- Memory usage grows linearly with active connections
- Difficult to implement load balancing with sticky sessions

## Proposed Refactoring
Replace in-memory state management with:
- Redis for distributed connection state storage
- Pub/Sub pattern for message broadcasting across instances
- Connection state persistence for graceful restarts
- Improved error handling and connection recovery

## Benefits
- Enables horizontal scaling of Chat Service instances
- Better fault tolerance and resilience
- Reduced memory footprint per instance
- Easier maintenance and deployment

## Implementation Plan
1. Integrate Redis for connection state management
2. Implement pub/sub for cross-instance message broadcasting
3. Add connection state persistence mechanisms
4. Update WebSocket handler architecture
5. Test horizontal scaling scenarios
```

### Issue 6: Standardize Error Handling Across Services
```
---
name: Standardize Error Handling and Response Formats
about: Inconsistent error handling makes debugging difficult
title: '[TECH DEBT] Standardize error handling and response formats across all services'
labels: tech-debt, api, error-handling
assignees: ''

---

## Technical Debt Description
Different services use inconsistent error response formats, making client-side error handling complex and debugging difficult.

## Current Issues
- User Service returns different error structures than other services
- Missing standardized HTTP status codes usage
- Inconsistent error message formats
- Lack of structured error responses with error codes

## Proposed Standardization
Implement unified error handling with:
- Standard JSON error response format
- Consistent HTTP status code usage
- Error codes for programmatic error handling
- Structured error details for debugging
- Centralized error logging

## Standard Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Descriptive error message",
    "details": {
      "field": "specific_field",
      "issue": "validation_issue"
    },
    "timestamp": "2026-01-16T10:30:00Z"
  }
}
```

## Implementation Steps
1. Define standard error response schema
2. Create shared error handling middleware
3. Update each service to use standardized format
4. Document error codes and their meanings
5. Update frontend error handling to match new format
```

## 📚 Documentation Improvements

### Issue 7: Improve API Documentation with OpenAPI/Swagger
```
---
name: Add Comprehensive API Documentation with OpenAPI Specification
about: Current API documentation is incomplete and scattered
title: '[DOCS] Implement comprehensive OpenAPI/Swagger documentation'
labels: documentation, api, swagger
assignees: ''

---

## Documentation Gap
Current API documentation is minimal and scattered across README files, making it difficult for developers to understand and use the APIs effectively.

## Proposed Solution
Implement OpenAPI 3.0 specifications for all services:
- Generate interactive API documentation
- Provide example requests and responses
- Document authentication requirements
- Include rate limiting and error response information
- Enable API testing directly from documentation

## Services to Document
- [ ] Gateway Service API
- [ ] User Service API
- [ ] Chat Service API (including WebSocket endpoints)
- [ ] Message Service API

## Implementation Approach
1. Add OpenAPI annotations to existing code
2. Generate Swagger UI documentation
3. Host documentation alongside services
4. Automate documentation generation in CI pipeline
5. Add documentation testing to prevent drift

## Acceptance Criteria
- [ ] All public API endpoints are documented
- [ ] Interactive documentation is accessible via web interface
- [ ] Examples are provided for common use cases
- [ ] Authentication flows are clearly documented
- [ ] Documentation stays synchronized with code changes
```

### Issue 8: Create Developer Onboarding Guide
```
---
name: Create Comprehensive Developer Onboarding Guide
about: New contributors struggle with complex setup process
title: '[DOCS] Create comprehensive developer onboarding guide'
labels: documentation, onboarding, getting-started
assignees: ''

---

## Documentation Need
New developers face significant challenges setting up the development environment due to the polyglot nature and complex microservices architecture.

## Proposed Guide Contents
1. **Prerequisites Checklist**
   - Required tools and versions
   - System requirements
   - Account setup (GitHub, Docker Hub, etc.)

2. **Quick Start Guide**
   - Repository cloning and initial setup
   - First-time Docker Compose startup
   - Verifying all services are running
   - Running basic tests

3. **Architecture Overview**
   - Service relationships and communication patterns
   - Data flow diagrams
   - Technology stack breakdown

4. **Development Workflows**
   - Working on individual services locally
   - Debugging cross-service issues
   - Testing strategies and commands
   - Common development tasks

5. **Troubleshooting Guide**
   - Common setup issues and solutions
   - Service-specific debugging techniques
   - Log analysis and monitoring
   - Performance optimization tips

## Implementation Plan
1. Create structured documentation in docs/ directory
2. Include code examples and configuration samples
3. Add visual diagrams for architecture understanding
4. Provide troubleshooting flowcharts
5. Regular updates based on contributor feedback
```

## ⚙️ CI/CD Pipeline Improvements

### Issue 9: Optimize CI Pipeline Build Times
```
---
name: Optimize CI Pipeline Build Times Through Better Caching
about: Current CI builds are slow due to inefficient caching strategies
title: '[CI/CD] Optimize build times through improved caching strategies'
labels: ci-cd, performance, optimization
assignees: ''

---

## Performance Issue
Current CI pipeline builds take excessive time (15-20 minutes) due to suboptimal caching and redundant operations.

## Current Bottlenecks
- Inefficient dependency caching for each service
- Redundant Docker layer rebuilding
- Sequential test execution when parallelization possible
- Missing build artifact caching between runs

## Optimization Goals
Reduce total build time from ~20 minutes to <8 minutes through:

## Proposed Improvements

### 1. Enhanced Caching Strategy
- Better cache key strategies using file hashes
- Separate caching for build vs runtime dependencies
- Cross-run artifact caching for incremental builds

### 2. Parallel Job Execution
- Run service tests in parallel matrix jobs
- Parallelize Docker builds where possible
- Concurrent security scanning and linting

### 3. Docker Optimization
- Multi-stage build optimizations
- Better layer caching with buildkit
- Base image pre-caching strategies

### 4. Selective Testing
- Run only affected service tests on changes
- Skip integration tests for documentation-only changes
- Fast-fail strategies for early error detection

## Implementation Metrics
- Current average build time: 18 minutes
- Target build time: <8 minutes
- Cache hit rate improvement target: >80%
```

### Issue 10: Add Automated Security Scanning to CI Pipeline
```
---
name: Enhance CI Pipeline with Comprehensive Security Scanning
about: Current security scanning is minimal and manual
title: '[CI/CD] Implement comprehensive automated security scanning'
labels: ci-cd, security, devsecops
assignees: ''

---

## Security Gap
Current CI pipeline lacks comprehensive automated security scanning, relying mostly on manual checks and basic dependency scanning.

## Proposed Security Scanning Suite

### 1. Static Application Security Testing (SAST)
- **Python Services**: Bandit, Semgrep
- **JavaScript Services**: ESLint security plugin, NodeJsScan
- **Go Services**: Gosec
- **Rust Services**: Clippy security lints

### 2. Software Composition Analysis (SCA)
- Dependency vulnerability scanning for all services
- License compliance checking
- Outdated dependency detection

### 3. Container Security Scanning
- Docker image vulnerability scanning
- Base image security assessment
- Runtime security configuration checks

### 4. Infrastructure Security
- Dockerfile security best practices
- Kubernetes manifest security (future)
- Network security configuration validation

## Implementation Plan

### Phase 1: Basic Security Scanning
- Integrate existing tools (safety, bandit) into CI
- Add dependency scanning for all services
- Implement basic container scanning

### Phase 2: Advanced Security Features
- Add SAST tools for each language
- Implement security gate policies
- Add security dashboard reporting

### Phase 3: Compliance and Reporting
- Generate security compliance reports
- Implement security scorecards
- Add automated security notifications

## Acceptance Criteria
- [ ] All services scanned for known vulnerabilities
- [ ] Security gates prevent deployment of critical issues
- [ ] Security reports generated automatically
- [ ] Zero-day vulnerability detection implemented
- [ ] Security scanning integrated into PR workflow
```

## Usage Instructions

To create these issues:

1. **Navigate to your GitHub repository**
2. **Go to the Issues tab**
3. **Click "New Issue"**
4. **Copy the content between the ``` markers for each issue**
5. **Paste into the issue description**
6. **Fill in any additional details as needed**
7. **Submit the issue**

You can customize the titles, labels, and assignees based on your team's workflow and preferences.