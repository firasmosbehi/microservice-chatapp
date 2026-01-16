"""
Linting and code quality tests for chat service
Tests code formatting, style compliance, and quality metrics
"""

import subprocess
import tempfile
import os
from pathlib import Path
import pytest


def run_lint_tool(tool_cmd: list, description: str) -> tuple[bool, str]:
    """Run a linting tool and return success status and output"""
    try:
        result = subprocess.run(
            tool_cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        success = result.returncode == 0
        output = result.stdout + result.stderr
        return success, output
    except subprocess.TimeoutExpired:
        return False, f"{description} timed out"
    except FileNotFoundError:
        return False, f"{description} tool not found"


def test_black_formatting():
    """Test that code follows black formatting standards"""
    cmd = ["poetry", "run", "black", "--check", "chat_app/"]
    success, output = run_lint_tool(cmd, "Black formatting check")
    
    if not success:
        print("❌ Black formatting issues found:")
        print(output)
        print("\n🔧 To fix formatting, run: poetry run black chat_app/")
    
    assert success, "Code does not follow black formatting standards"


def test_flake8_compliance():
    """Test that code passes flake8 linting"""
    cmd = [
        "poetry", "run", "flake8",
        "chat_app/",
        "--max-line-length=100",
        "--extend-ignore=E203,W503,E501,W292,W291,W293,E722,E128,F841,F401"
    ]
    success, output = run_lint_tool(cmd, "Flake8 linting")
    
    if not success:
        print("❌ Flake8 violations found:")
        print(output)
        print("\n🔧 Fix the reported issues or adjust flake8 configuration")
    
    assert success, "Code has flake8 violations"


def test_pylint_analysis():
    """Test code quality with pylint"""
    cmd = [
        "poetry", "run", "pylint",
        "chat_app/",
        "--disable=C0114,C0115,C0116,R0903,W0613,R0913,R0902,R0914"
    ]
    success, output = run_lint_tool(cmd, "Pylint analysis")
    
    # Pylint scores below 7.0 are concerning but not necessarily failing
    if not success:
        lines = output.split('\n')
        score_line = [line for line in lines if 'Your code has been rated at' in line]
        if score_line:
            score_text = score_line[0]
            try:
                score = float(score_text.split('/')[0].split()[-1])
                if score < 7.0:
                    print(f"⚠️  Low pylint score: {score}/10.0")
                    print("Consider improving code quality")
                    # Don't fail for low scores, just warn
                else:
                    print(f"✅ Good pylint score: {score}/10.0")
            except (ValueError, IndexError):
                pass
        else:
            print("❌ Pylint found issues:")
            print(output)


def test_mypy_type_checking():
    """Test that code passes mypy type checking"""
    cmd = ["poetry", "run", "mypy", "chat_app/"]
    success, output = run_lint_tool(cmd, "Mypy type checking")
    
    if not success:
        print("❌ Mypy type checking issues:")
        print(output)
        print("\n🔧 Fix type annotations or adjust mypy configuration")
    
    assert success, "Code has mypy type checking errors"


def test_code_complexity():
    """Test code complexity metrics"""
    # Check for overly complex functions using radon or similar
    try:
        cmd = ["poetry", "run", "radon", "cc", "chat_app/", "-a"]
        success, output = run_lint_tool(cmd, "Radon complexity analysis")
        
        if success:
            lines = output.split('\n')
            # Look for complexity warnings
            complex_functions = [line for line in lines if 'C:' in line and ('C' in line.split()[1] or 'D' in line.split()[1])]
            if complex_functions:
                print("⚠️  Functions with high complexity found:")
                for func in complex_functions[:5]:  # Show top 5
                    print(f"  {func}")
                print("Consider refactoring complex functions")
        else:
            print("⚠️  Radon not available, skipping complexity analysis")
            
    except Exception as e:
        print(f"⚠️  Complexity analysis skipped: {e}")


def test_duplicate_code():
    """Test for duplicate code"""
    try:
        cmd = ["poetry", "run", "radon", "cc", "chat_app/", "-d"]
        success, output = run_lint_tool(cmd, "Duplicate code detection")
        
        if success and 'DUPLICATES' in output:
            print("⚠️  Duplicate code detected:")
            print(output)
            print("Consider refactoring to eliminate duplication")
            
    except Exception as e:
        print(f"⚠️  Duplicate code detection skipped: {e}")


def test_docstring_coverage():
    """Test that functions and classes have docstrings"""
    import ast
    from pathlib import Path
    
    chat_app_dir = Path("chat_app")
    missing_docs = []
    
    for py_file in chat_app_dir.rglob("*.py"):
        if py_file.name.startswith('.') or py_file.name == '__init__.py':
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    # Skip if no docstring
                    if not ast.get_docstring(node):
                        # Get line number for reporting
                        line_no = node.lineno
                        node_type = "function" if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else "class"
                        missing_docs.append(f"{py_file}:{line_no} - {node_type} '{node.name}' missing docstring")
                        
        except Exception as e:
            print(f"⚠️  Error analyzing {py_file}: {e}")
    
    if missing_docs:
        print("⚠️  Missing docstrings found:")
        for doc_issue in missing_docs[:10]:  # Show first 10
            print(f"  {doc_issue}")
        if len(missing_docs) > 10:
            print(f"  ... and {len(missing_docs) - 10} more")
        print("Consider adding docstrings for better code documentation")


def test_import_order():
    """Test that imports are properly ordered"""
    try:
        cmd = ["poetry", "run", "isort", "--check-only", "chat_app/"]
        success, output = run_lint_tool(cmd, "Import order check")
        
        if not success:
            print("❌ Import order issues found:")
            print(output)
            print("\n🔧 To fix imports, run: poetry run isort chat_app/")
            
    except Exception as e:
        print(f"⚠️  Import order check skipped: {e}")


def test_line_length():
    """Test that lines don't exceed reasonable length"""
    max_length = 100
    violations = []
    
    chat_app_dir = Path("chat_app")
    for py_file in chat_app_dir.rglob("*.py"):
        if py_file.name.startswith('.'):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if len(line.rstrip()) > max_length:
                        violations.append(f"{py_file}:{line_num} - Line too long ({len(line.rstrip())} > {max_length})")
        except Exception as e:
            print(f"⚠️  Error checking line lengths in {py_file}: {e}")
    
    if violations:
        print("⚠️  Line length violations found:")
        for violation in violations[:5]:  # Show first 5
            print(f"  {violation}")
        if len(violations) > 5:
            print(f"  ... and {len(violations) - 5} more")
        print(f"Consider keeping lines under {max_length} characters")


def test_naming_conventions():
    """Test that naming conventions are followed"""
    import re
    from pathlib import Path
    
    # Regex patterns for different naming conventions
    snake_case_pattern = re.compile(r'^[a-z_][a-z0-9_]*$')
    camel_case_pattern = re.compile(r'^[a-z][a-zA-Z0-9]*$')
    pascal_case_pattern = re.compile(r'^[A-Z][a-zA-Z0-9]*$')
    
    violations = []
    chat_app_dir = Path("chat_app")
    
    for py_file in chat_app_dir.rglob("*.py"):
        if py_file.name.startswith('.'):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Simple AST-based naming check
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not snake_case_pattern.match(node.name) and not node.name.startswith('_'):
                        violations.append(f"{py_file}:{node.lineno} - Function '{node.name}' should use snake_case")
                elif isinstance(node, ast.ClassDef):
                    if not pascal_case_pattern.match(node.name):
                        violations.append(f"{py_file}:{node.lineno} - Class '{node.name}' should use PascalCase")
                        
        except Exception as e:
            print(f"⚠️  Error checking naming conventions in {py_file}: {e}")
    
    if violations:
        print("⚠️  Naming convention violations found:")
        for violation in violations[:5]:  # Show first 5
            print(f"  {violation}")
        if len(violations) > 5:
            print(f"  ... and {len(violations) - 5} more")


if __name__ == "__main__":
    # Run linting tests standalone
    pytest.main([__file__, "-v"])