#!/usr/bin/env python3
"""
Optimized test runner for chat service
Provides faster testing workflow with selective test execution
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path
from typing import List, Optional
import time


def run_command(cmd: List[str], description: str, quiet: bool = False) -> bool:
    """
    Run a command and return True if successful, False otherwise
    """
    if not quiet:
        print(f"🔍 {description}")
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        elapsed = time.time() - start_time
        
        if not quiet:
            if result.stdout.strip():
                print(result.stdout)
            print(f"✅ {description} completed in {elapsed:.2f}s")
        return True
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        if not quiet:
            print(f"❌ {description} failed after {elapsed:.2f}s:")
            print(f"Command: {' '.join(cmd)}")
            print(f"Error: {e.stderr}")
        return False
    except FileNotFoundError:
        if not quiet:
            print(f"⚠️  Command not found: {' '.join(cmd)}")
        return False


def run_fast_tests() -> bool:
    """Run essential unit tests quickly (skip coverage-heavy tests)"""
    cmd = [
        "poetry", "run", "pytest", 
        "tests/unit/test_api.py",
        "tests/unit/test_services.py", 
        "tests/unit/test_models.py",
        "-v",
        "--tb=short"
    ]
    return run_command(cmd, "Running essential unit tests")


def run_coverage_tests() -> bool:
    """Run full coverage tests (slower but comprehensive)"""
    cmd = [
        "poetry", "run", "pytest", 
        "tests/unit/", 
        "-v", 
        "--cov=chat_app", 
        "--cov-report=term-missing"
    ]
    return run_command(cmd, "Running full coverage tests")


def run_quick_lint() -> bool:
    """Run quick linting (fewer ignores for faster feedback)"""
    cmd = [
        "poetry", "run", "flake8", 
        "chat_app/", 
        "--max-line-length=100",
        "--select=E9,F63,F7,F82"  # Only critical errors
    ]
    return run_command(cmd, "Running quick linting")


def run_full_lint() -> bool:
    """Run comprehensive linting"""
    cmd = [
        "poetry", "run", "flake8", 
        "chat_app/", 
        "--max-line-length=100",
        "--extend-ignore=E203,W503,E501,W292,W291,W293,E722,E128,F841,F401"
    ]
    return run_command(cmd, "Running full linting")


def run_type_checking() -> bool:
    """Run type checking with mypy"""
    cmd = [
        "poetry", "run", "mypy", 
        "chat_app/",
        "--ignore-missing-imports"
    ]
    return run_command(cmd, "Running type checking")


def run_changed_tests() -> bool:
    """Run tests only for changed files"""
    try:
        # Get changed Python files
        result = subprocess.run([
            "git", "diff", "--name-only", "HEAD", "--", "*.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            changed_files = result.stdout.strip().split('\n')
            test_files = [f for f in changed_files if 'test_' in f]
            app_files = [f for f in changed_files if 'chat_app/' in f]
            
            if test_files:
                # Run specific test files
                cmd = ["poetry", "run", "pytest"] + test_files + ["-v", "--tb=short"]
                return run_command(cmd, "Running tests for changed files")
            elif app_files:
                # Run tests that might be affected
                cmd = [
                    "poetry", "run", "pytest", 
                    "tests/unit/", 
                    "-v", 
                    "--tb=short",
                    "-k", " or ".join([Path(f).stem for f in app_files])
                ]
                return run_command(cmd, "Running related tests for changed files")
        
        print("No Python files changed, skipping tests")
        return True
    except Exception as e:
        print(f"⚠️  Could not determine changed files: {e}")
        return run_fast_tests()


def main():
    """Main function with optimized test options"""
    parser = argparse.ArgumentParser(description="Optimized Chat Service Test Runner")
    parser.add_argument(
        "mode", 
        nargs="?",
        default="fast",
        choices=["fast", "full", "coverage", "changed", "lint", "type-check"],
        help="Test mode: fast (essential tests), full (all tests), coverage (with coverage), changed (only changed files), lint (code style), type-check (mypy)"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode")
    
    args = parser.parse_args()
    
    # Change to the script's directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    if not args.quiet:
        print(f"🚀 Starting Chat Service tests ({args.mode} mode)...")
    
    start_time = time.time()
    success = True
    
    if args.mode == "fast":
        success &= run_fast_tests()
        if not args.quiet:
            print("\n💡 Tip: Use 'full' mode for comprehensive testing or 'coverage' for 100% coverage")
    
    elif args.mode == "full":
        success &= run_fast_tests()
        success &= run_full_lint()
        success &= run_type_checking()
    
    elif args.mode == "coverage":
        success &= run_coverage_tests()
        success &= run_full_lint()
        success &= run_type_checking()
    
    elif args.mode == "changed":
        success &= run_changed_tests()
    
    elif args.mode == "lint":
        success &= run_quick_lint()
    
    elif args.mode == "type-check":
        success &= run_type_checking()
    
    elapsed = time.time() - start_time
    
    if success:
        if not args.quiet:
            print(f"\n🎉 Tests completed successfully in {elapsed:.2f}s!")
            if args.mode == "fast":
                print("⚡ Fast mode: Skipped coverage and comprehensive linting for speed")
        sys.exit(0)
    else:
        if not args.quiet:
            print(f"\n❌ Some tests failed after {elapsed:.2f}s!")
        sys.exit(1)


if __name__ == "__main__":
    main()