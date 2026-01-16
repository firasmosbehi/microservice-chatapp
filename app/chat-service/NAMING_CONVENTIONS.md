# Python Project Naming Conventions

## File Naming Standards

### 1. Python Source Files
- **snake_case** for all Python files
- Use descriptive names that clearly indicate purpose
- Examples: `user_service.py`, `message_handler.py`, `auth_utils.py`

### 2. Test Files
- **Pattern**: `test_<module_or_function_name>.py`
- Group related tests in directories:
  - `tests/unit/` - Unit tests
  - `tests/integration/` - Integration tests  
  - `tests/security/` - Security tests
  - `tests/linting/` - Linting/code quality tests

### 3. Script Files
- **Pattern**: `<action>_<target>.py` or `<action>.py`
- Examples: `run_tests.py`, `deploy_service.py`, `generate_docs.py`

### 4. Configuration Files
- Use established conventions:
  - `pyproject.toml` (Poetry/PEP 621)
  - `requirements.txt` (pip)
  - `.env` (environment variables)

## Specific Recommendations for Current Files

### Test Files to Rename:
1. `test_coverage.py` → `test_code_coverage.py` (more descriptive)
2. `test_final_coverage.py` → `test_full_coverage.py` (clearer meaning)
3. `test_100_percent_coverage.py` → `test_complete_coverage.py` (avoid numbers in names)

### Script Files:
- `run_tests.py` ✓ (Good - follows convention)
- `run_tests_optimized.py` → `run_tests_fast.py` (more intuitive)
- `run_tests.sh` ✓ (Shell script - acceptable)

## Directory Structure
```
chat-service/
├── chat_app/                 # Main application package
│   ├── __init__.py
│   ├── app.py               # Main application entry point
│   ├── models.py            # Data models
│   ├── routes.py            # API routes
│   ├── services.py          # Business logic
│   └── websocket.py         # WebSocket handlers
├── tests/
│   ├── unit/                # Unit tests
│   │   ├── test_api.py
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   ├── test_code_coverage.py
│   │   ├── test_full_coverage.py
│   │   └── test_complete_coverage.py
│   ├── integration/         # Integration tests
│   ├── security/            # Security tests
│   └── linting/             # Linting tests
├── scripts/                 # Utility scripts (optional)
│   ├── run_tests.py
│   └── run_tests_fast.py
└── config/                  # Configuration files (optional)
```

## Best Practices

1. **Consistency**: Apply naming conventions uniformly across the project
2. **Clarity**: Names should clearly indicate file purpose
3. **Brevity**: Keep names concise but descriptive
4. **Standards**: Follow Python community conventions (PEP 8)
5. **Tool Compatibility**: Ensure names work well with development tools

## Automated Enforcement

- Use pre-commit hooks to enforce naming conventions
- Configure linters to check file names
- Document conventions in CONTRIBUTING.md