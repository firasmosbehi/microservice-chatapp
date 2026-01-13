#!/bin/bash

# User Service Test Runner
# Runs all unit tests for the User Service

set -e

echo "🧪 Running User Service Unit Tests"
echo "=================================="

cd "$(dirname "$0")"

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Run unit tests
echo "🏃 Running unit tests..."
npm test

# Run coverage report
echo "📊 Generating coverage report..."
npm run test:coverage

echo "✅ User Service tests completed successfully!"