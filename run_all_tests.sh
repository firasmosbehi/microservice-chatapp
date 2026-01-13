#!/bin/bash

# Comprehensive Test Runner for All Microservices
# Runs unit tests for all services and provides summary

set -e  # Exit on any error

echo "🚀 Starting Comprehensive Microservices Test Suite..."
echo "====================================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track test results
PASSED_SERVICES=0
FAILED_SERVICES=0
TOTAL_SERVICES=4

# Function to run tests for a service
run_service_tests() {
    local service_name=$1
    local service_dir=$2
    local test_command=$3
    local setup_command=$4
    
    echo -e "${BLUE}📋 Testing $service_name${NC}"
    echo "----------------------------------------"
    
    # Navigate to service directory
    cd "$service_dir" || { echo -e "${RED}❌ Failed to navigate to $service_dir${NC}"; return 1; }
    
    # Run setup if provided
    if [ -n "$setup_command" ]; then
        echo "🔧 Running setup: $setup_command"
        eval "$setup_command" || { echo -e "${RED}❌ Setup failed for $service_name${NC}"; return 1; }
    fi
    
    # Run tests
    echo "🏃 Running tests: $test_command"
    if eval "$test_command"; then
        echo -e "${GREEN}✅ $service_name tests passed${NC}"
        ((PASSED_SERVICES++))
        return 0
    else
        echo -e "${RED}❌ $service_name tests failed${NC}"
        ((FAILED_SERVICES++))
        return 1
    fi
}

# Function to check if service is running
check_service_running() {
    local port=$1
    local service_name=$2
    
    if nc -z localhost "$port" 2>/dev/null; then
        echo -e "${GREEN}✅ $service_name is running on port $port${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  $service_name is not running on port $port${NC}"
        return 1
    fi
}

echo "🔍 Pre-flight Checks"
echo "==================="

# Check if services are running
check_service_running 3001 "User Service"
check_service_running 3002 "Chat Service" 
check_service_running 3003 "Message Service"
check_service_running 8000 "Gateway Service"

echo
echo "🧪 Running Unit Tests"
echo "===================="

# Test User Service (Node.js)
run_service_tests \
    "User Service" \
    "../app/user-service" \
    "npm test" \
    "npm install"

echo

# Test Chat Service (Python)  
run_service_tests \
    "Chat Service" \
    "../app/chat-service" \
    "python -m pytest tests/ -v" \
    "pip install -r requirements.txt"

echo

# Test Message Service (Go)
run_service_tests \
    "Message Service" \
    "../app/message-service" \
    "go test -v ./..." \
    "go mod tidy"

echo

# Test Gateway Service (Rust)
run_service_tests \
    "Gateway Service" \
    "../app/gateway-service" \
    "cargo test" \
    ""

echo

# Summary
echo "📊 Test Results Summary"
echo "======================"
echo -e "${GREEN}✅ Passed Services: $PASSED_SERVICES${NC}"
echo -e "${RED}❌ Failed Services: $FAILED_SERVICES${NC}"
echo -e "📋 Total Services: $TOTAL_SERVICES"
echo

# Calculate percentage
if [ $TOTAL_SERVICES -gt 0 ]; then
    SUCCESS_RATE=$((PASSED_SERVICES * 100 / TOTAL_SERVICES))
    echo "📈 Success Rate: ${SUCCESS_RATE}%"
fi

echo

# Final verdict
if [ $FAILED_SERVICES -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Microservices are ready for deployment.${NC}"
    exit 0
else
    echo -e "${RED}💥 Some tests failed. Please check the output above for details.${NC}"
    exit 1
fi