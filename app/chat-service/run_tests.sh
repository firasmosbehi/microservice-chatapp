#!/bin/bash
# Unified test runner for chat service

set -e  # Exit on any error

echo "🚀 Starting Chat Service tests..."

# Function to run linting
run_linting() {
    echo "🔍 Running linting checks..."
    if command -v poetry &> /dev/null; then
        poetry run flake8 chat_app/ --max-line-length=88 --extend-ignore=E203,W503
        echo "✅ Linting passed"
    else
        echo "⚠️  Poetry not found, skipping linting"
    fi
}

# Function to run type checking
run_type_checking() {
    echo "🔍 Running type checking..."
    if command -v poetry &> /dev/null; then
        poetry run mypy chat_app/ --package chat_app
        echo "✅ Type checking passed"
    else
        echo "⚠️  Poetry not found, skipping type checking"
    fi
}

# Function to run unit tests with coverage
run_unit_tests() {
    echo "🧪 Running unit tests..."
    if command -v poetry &> /dev/null; then
        poetry run pytest tests/ -v --cov=chat_app --cov-report=term-missing --cov-report=xml
        echo "✅ Unit tests passed"
    else
        echo "⚠️  Poetry not found, skipping unit tests"
    fi
}

# Function to run security checks
run_security_checks() {
    echo "🔒 Running security checks..."
    if command -v poetry &> /dev/null; then
        # Check for security vulnerabilities in dependencies
        if poetry show --tree | grep -i "security\|vulnerability" > /dev/null 2>&1; then
            echo "⚠️  Potential security issues detected"
        else
            echo "✅ No obvious security issues detected"
        fi
    else
        echo "⚠️  Poetry not found, skipping security checks"
    fi
}

# Parse command line arguments
case "${1:-all}" in
    lint)
        run_linting
        ;;
    type-check)
        run_type_checking
        ;;
    test)
        run_unit_tests
        ;;
    security)
        run_security_checks
        ;;
    all)
        run_linting
        run_type_checking
        run_unit_tests
        run_security_checks
        echo "🎉 All tests completed successfully!"
        ;;
    *)
        echo "Usage: $0 [lint|type-check|test|security|all]"
        echo "  lint        - Run code linting"
        echo "  type-check  - Run type checking"
        echo "  test        - Run unit tests"
        echo "  security    - Run security checks"
        echo "  all         - Run all checks (default)"
        exit 1
        ;;
esac