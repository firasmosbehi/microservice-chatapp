#!/usr/bin/env python3
"""
Test runner for chat service
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run all tests with coverage"""
    print("🧪 Running Chat Service Unit Tests...")
    print("=" * 40)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Run pytest with coverage
    cmd = [
        "poetry", "run", "pytest",
        "-v",
        "--cov=chat_service",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "tests/"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/")
        return True
    except subprocess.CalledProcessError:
        print("\n❌ Some tests failed!")
        return False

def run_linting():
    """Run code quality checks"""
    print("\n🔍 Running code quality checks...")
    print("=" * 30)
    
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Run black (formatting)
    print("Checking code formatting with black...")
    black_result = subprocess.run(["poetry", "run", "black", "--check", "chat_service/", "tests/"])
    
    # Run flake8 (linting)
    print("Running linting checks with flake8...")
    flake8_result = subprocess.run(["poetry", "run", "flake8", "chat_service/", "tests/"])
    
    return black_result.returncode == 0 and flake8_result.returncode == 0

def main():
    """Main test runner"""
    print("🚀 Chat Service Test Suite")
    print("=" * 30)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found!")
        print("Please run this script from the chat-service directory.")
        sys.exit(1)
    
    # Install dependencies if needed
    print("📦 Checking dependencies...")
    subprocess.run(["poetry", "install", "--only=main"], check=True)
    subprocess.run(["poetry", "install", "--only=dev"], check=True)
    
    # Run tests
    tests_passed = run_tests()
    
    # Run linting
    linting_passed = run_linting()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary")
    print("=" * 50)
    print(f"Tests: {'✅ PASSED' if tests_passed else '❌ FAILED'}")
    print(f"Linting: {'✅ PASSED' if linting_passed else '❌ FAILED'}")
    
    if tests_passed and linting_passed:
        print("\n🎉 All checks passed!")
        sys.exit(0)
    else:
        print("\n💥 Some checks failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()