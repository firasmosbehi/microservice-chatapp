#!/bin/bash

# Message Service Test Runner
# Runs all Go tests with proper setup and reporting

set -e

echo "🚀 Starting Message Service Unit Tests..."
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Change to message service directory
cd "$(dirname "$0")/.."

# Function to run tests
run_go_tests() {
    local test_pattern=$1
    local description=$2
    
    echo -e "${BLUE}🧪 Running $description${NC}"
    echo "----------------------------------------"
    
    # Run Go tests with coverage
    if go test -v -coverprofile=coverage.out "./tests/$test_pattern" 2>&1; then
        echo -e "${GREEN}✅ $description tests passed${NC}"
        return 0
    else
        echo -e "${RED}❌ $description tests failed${NC}"
        return 1
    fi
}

# Check if Go is installed
if ! command -v go &> /dev/null; then
    echo -e "${RED}❌ Go is not installed${NC}"
    exit 1
fi

# Check if dependencies are installed
echo -e "${BLUE}📦 Checking dependencies...${NC}"
if ! go mod tidy; then
    echo -e "${RED}❌ Failed to tidy Go modules${NC}"
    exit 1
fi

# Test files to run
test_files=(
    "handlers_test.go:Handler tests"
    "models_test.go:Model tests" 
    "utils_test.go:Utility tests"
    "main_test.go:Integration tests"
)

# Track results
passed=0
failed=0

# Run each test file
for test_entry in "${test_files[@]}"; do
    IFS=':' read -r test_file description <<< "$test_entry"
    
    if [ -f "tests/$test_file" ]; then
        if run_go_tests "$test_file" "$description"; then
            ((passed++))
        else
            ((failed++))
        fi
        echo
    else
        echo -e "${YELLOW}⚠️  Skipping $test_file (file not found)${NC}"
    fi
done

# Summary
echo "========================================"
echo -e "${BLUE}📊 Test Results Summary${NC}"
echo "========================================"
echo -e "${GREEN}✅ Passed: $passed${NC}"
echo -e "${RED}❌ Failed: $failed${NC}"
echo "📋 Total: $((passed + failed))"

# Generate coverage report
if [ -f coverage.out ]; then
    echo
    echo -e "${BLUE}📈 Coverage Report:${NC}"
    go tool cover -func=coverage.out | tail -1
    
    # Generate HTML coverage report
    go tool cover -html=coverage.out -o coverage.html
    echo -e "${GREEN}📄 HTML coverage report saved to coverage.html${NC}"
fi

# Final result
if [ $failed -eq 0 ]; then
    echo
    echo -e "${GREEN}🎉 All Message Service tests passed!${NC}"
    exit 0
else
    echo
    echo -e "${RED}💥 $failed test file(s) failed${NC}"
    exit 1
fi