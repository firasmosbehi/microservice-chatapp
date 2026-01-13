#!/bin/bash

# Message Service Test Runner
# Runs all unit tests for the Message Service

set -e

echo "🧪 Running Message Service Unit Tests"
echo "====================================="

cd "$(dirname "$0")"

# Check if Go is available
if ! command -v go &> /dev/null; then
    echo "❌ Go is not installed"
    exit 1
fi

# Download dependencies
echo "📦 Downloading dependencies..."
go mod tidy

# Run unit tests
echo "🏃 Running unit tests..."
go test -v ./...

# Run tests with coverage
echo "📊 Running tests with coverage..."
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html

# Run race condition tests
echo "🔒 Running race condition tests..."
go test -race ./...

echo "✅ Message Service tests completed successfully!"