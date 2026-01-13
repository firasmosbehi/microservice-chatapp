#!/bin/bash

# Chat Service Test Runner
# Runs all unit tests for the Chat Service

set -e

echo "🧪 Running Chat Service Unit Tests"
echo "=================================="

cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed"
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run unit tests
echo "🏃 Running unit tests..."
python -m pytest tests/ -v --tb=short

# Run tests with coverage
echo "📊 Running tests with coverage..."
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term

echo "✅ Chat Service tests completed successfully!"