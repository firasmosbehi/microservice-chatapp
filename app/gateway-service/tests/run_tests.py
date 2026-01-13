#!/usr/bin/env python3
"""
Gateway Service Test Runner
Runs all unit tests with proper setup and reporting
"""

import subprocess
import sys
import os
from pathlib import Path

def run_gateway_tests():
    """Run all gateway service tests"""
    print("🚀 Starting Gateway Service Unit Tests...")
    print("=" * 45)
    
    # Change to gateway service directory
    gateway_dir = Path(__file__).parent.parent
    os.chdir(gateway_dir)
    
    # Set environment variables
    env = os.environ.copy()
    env.update({
        'PYTHONPATH': str(gateway_dir),
        'TESTING': 'true',
        'FLASK_ENV': 'testing'
    })
    
    # Test files to run
    test_files = [
        'tests/test_app.py'
    ]
    
    # Run pytest for each test file
    total_passed = 0
    total_failed = 0
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"⚠️  Skipping {test_file} (file not found)")
            continue
            
        print(f"\n🧪 Running tests in {test_file}")
        print("-" * 35)
        
        try:
            # Run pytest with coverage
            result = subprocess.run([
                sys.executable, '-m', 'pytest',
                test_file,
                '-v',
                '--tb=short',
                '--cov=.',
                '--cov-report=term-missing',
                '--disable-warnings'
            ], env=env, capture_output=True, text=True)
            
            # Print output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            
            if result.returncode == 0:
                print(f"✅ Tests in {test_file} passed!")
                total_passed += 1
            else:
                print(f"❌ Tests in {test_file} failed!")
                total_failed += 1
                
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
            total_failed += 1
    
    # Summary
    print("\n" + "=" * 45)
    print("📊 Test Results Summary")
    print("=" * 45)
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"📋 Total: {total_passed + total_failed}")
    
    if total_failed == 0:
        print("\n🎉 All Gateway Service tests passed!")
        return True
    else:
        print(f"\n💥 {total_failed} test file(s) failed")
        return False

def install_dependencies():
    """Install required test dependencies"""
    print("📦 Checking test dependencies...")
    
    required_packages = [
        'pytest',
        'pytest-cov',
        'flask',
        'requests',
        'unittest-mock'
    ]
    
    try:
        import pytest
        import flask
        print("✅ All dependencies are installed")
        return True
    except ImportError:
        print("⚠️  Installing missing dependencies...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + required_packages)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

if __name__ == "__main__":
    # Install dependencies if needed
    if not install_dependencies():
        sys.exit(1)
    
    # Run tests
    success = run_gateway_tests()
    sys.exit(0 if success else 1)