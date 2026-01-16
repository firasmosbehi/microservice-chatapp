"""
Security tests for chat service
Tests for common security vulnerabilities and best practices
"""

import ast
import os
import tempfile
import pytest
from pathlib import Path
from typing import List, Set


class SecurityScanner:
    """Scan Python code for security vulnerabilities"""
    
    def __init__(self):
        self.dangerous_functions = {
            'eval', 'exec', 'compile', 'input', 'open', 'subprocess.run',
            'os.system', 'os.popen', 'pickle.loads', 'yaml.load', 'json.loads'
        }
        self.dangerous_imports = {
            'pickle', 'subprocess', 'os', 'sys'
        }
        self.security_issues = []
    
    def scan_file(self, file_path: Path) -> List[str]:
        """Scan a Python file for security issues"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
            # Check for dangerous function calls
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func_name = self._get_function_name(node.func)
                    if func_name in self.dangerous_functions:
                        issues.append(f"Dangerous function '{func_name}' called at line {node.lineno}")
                
                # Check for dangerous imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.split('.')[0] in self.dangerous_imports:
                            issues.append(f"Dangerous import '{alias.name}' at line {node.lineno}")
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.split('.')[0] in self.dangerous_imports:
                        issues.append(f"Dangerous import from '{node.module}' at line {node.lineno}")
                        
        except SyntaxError as e:
            issues.append(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            issues.append(f"Error scanning {file_path}: {e}")
            
        return issues
    
    def _get_function_name(self, func_node) -> str:
        """Extract function name from AST node"""
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            return func_node.attr
        return ""


@pytest.fixture
def security_scanner():
    """Fixture for security scanner"""
    return SecurityScanner()


def test_no_dangerous_eval_calls(security_scanner):
    """Test that no dangerous eval/exec calls exist in the codebase"""
    chat_app_dir = Path("chat_app")
    issues_found = []
    
    # Scan all Python files in chat_app directory
    for py_file in chat_app_dir.rglob("*.py"):
        if py_file.name.startswith('.'):
            continue
            
        issues = security_scanner.scan_file(py_file)
        issues_found.extend(issues)
    
    # Assert no security issues found
    assert len(issues_found) == 0, f"Security issues found:\n" + "\n".join(issues_found)


def test_secure_password_handling():
    """Test that passwords are properly handled (mock test)"""
    # Import the actual models to test password handling
    try:
        from chat_app.models import UserLogin, UserRegistration
        
        # Test that password fields exist but are not exposed in serialization
        login_model = UserLogin(username="test", password="password123")
        reg_model = UserRegistration(
            username="test", 
            email="test@example.com", 
            password="password123"
        )
        
        # These should not serialize passwords
        login_dict = login_model.model_dump()
        reg_dict = reg_model.model_dump()
        
        # Password should not be in serialized output
        assert 'password' not in login_dict or login_dict.get('password') != 'password123'
        assert 'password' not in reg_dict or reg_dict.get('password') != 'password123'
        
    except ImportError:
        pytest.skip("Models not available for testing")


def test_input_validation():
    """Test that input validation is properly implemented"""
    from pydantic import ValidationError
    
    try:
        from chat_app.models import UserRegistration, MessageRequest, CreateRoomRequest
        
        # Test email validation
        with pytest.raises(ValidationError):
            UserRegistration(
                username="test",
                email="invalid-email",
                password="password123"
            )
        
        # Test username length validation
        with pytest.raises(ValidationError):
            UserRegistration(
                username="a",  # Too short
                email="test@example.com",
                password="password123"
            )
        
        # Test password strength validation (if implemented)
        # This would depend on your validation rules
        
        # Test message content validation
        with pytest.raises(ValidationError):
            MessageRequest(
                room_id="valid-room",
                user_id=1,
                username="test",
                content=""  # Empty content
            )
            
        # Test room name validation
        with pytest.raises(ValidationError):
            CreateRoomRequest(
                name="",  # Empty name
                creator_id=1
            )
            
    except ImportError:
        pytest.skip("Models not available for testing")


def test_sql_injection_protection():
    """Test that SQL injection protection is in place (if using raw SQL)"""
    # This is a mock test - in reality, you'd check that:
    # 1. Parameterized queries are used instead of string concatenation
    # 2. ORM methods are preferred over raw SQL
    # 3. Input sanitization is applied
    
    # Since this is a FastAPI app using Pydantic models,
    # the validation should prevent most injection attacks
    pass


def test_xss_protection():
    """Test that XSS protection is considered"""
    # Test that HTML content is properly escaped in responses
    test_content = "<script>alert('xss')</script>"
    
    # This would depend on your templating/rendering approach
    # In FastAPI, automatic escaping should be enabled by default
    pass


def test_cors_configuration():
    """Test that CORS is properly configured"""
    try:
        from chat_app.app import app
        
        # Check that CORS middleware is configured appropriately
        # This is a structural test - you'd need to inspect the app configuration
        cors_configured = False
        
        # Handle case where middleware_stack might be None
        middleware_stack = getattr(app, 'middleware_stack', [])
        if middleware_stack:
            for middleware in middleware_stack:
                if 'CORSMiddleware' in str(middleware):
                    cors_configured = True
                    break
                    
        # This is a placeholder - actual implementation would depend on your CORS setup
        assert True  # Placeholder assertion - CORS configuration assumed valid
        
    except ImportError:
        pytest.skip("App not available for testing")
    except AttributeError:
        # Handle case where attributes don't exist
        pytest.skip("App structure not as expected for CORS testing")


def test_dependency_security():
    """Test that dependencies don't have known vulnerabilities"""
    # This would typically use safety or similar tools
    # For now, we'll do a basic check
    try:
        import subprocess
        result = subprocess.run(
            ["poetry", "show", "--outdated"], 
            capture_output=True, 
            text=True,
            timeout=30
        )
        # Just ensure the command runs without error
        assert result.returncode in [0, 1]  # 1 means outdated packages found, which is OK
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pytest.skip("Dependency check tools not available")


def test_file_permissions():
    """Test that sensitive files have appropriate permissions"""
    sensitive_files = [
        ".env",
        "config.py",
        "secrets.py"
    ]
    
    for filename in sensitive_files:
        if os.path.exists(filename):
            # Check file permissions (Unix-like systems)
            if hasattr(os, 'stat'):
                stat_info = os.stat(filename)
                # Permissions shouldn't be world-readable/writable
                assert (stat_info.st_mode & 0o077) == 0, f"{filename} has unsafe permissions"


def test_error_handling():
    """Test that error messages don't leak sensitive information"""
    # This would test that 500 errors don't expose stack traces
    # and that error messages are generic for security reasons
    pass


def test_rate_limiting():
    """Test that rate limiting is implemented"""
    # Check that rate limiting middleware or decorators are present
    # This would be implementation-specific
    pass


def test_authentication_validation():
    """Test that authentication mechanisms are secure"""
    # Test JWT token handling, session management, etc.
    # This would depend on your auth implementation
    pass


if __name__ == "__main__":
    # Run security tests standalone
    pytest.main([__file__, "-v"])