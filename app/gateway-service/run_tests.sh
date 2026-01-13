#!/bin/bash

# Gateway Service Test Runner
# Runs all unit tests for the Gateway Service

set -e

echo "🧪 Running Gateway Service Unit Tests"
echo "====================================="

cd "$(dirname "$0")"

# Check if Cargo/Rust is available
if ! command -v cargo &> /dev/null; then
    echo "❌ Rust/Cargo is not installed"
    exit 1
fi

# Run unit tests
echo "🏃 Running unit tests..."
cargo test

# Run tests with verbose output
echo "📢 Running tests with verbose output..."
cargo test -- --nocapture

# Run specific test categories
echo "🔬 Running integration tests..."
cargo test --test integration

echo "✅ Gateway Service tests completed successfully!"