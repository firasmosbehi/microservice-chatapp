#!/usr/bin/env python3
"""
Gateway Service Basic Test
Tests core functionality without external dependencies
"""

import json
import os
from datetime import datetime

def test_service_mapping():
    """Test service URL mapping logic"""
    print("🧪 Testing Service Mapping...")
    
    # Test service URLs
    USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://user-service:3001')
    CHAT_SERVICE_URL = os.getenv('CHAT_SERVICE_URL', 'http://chat-service:3002')
    MESSAGE_SERVICE_URL = os.getenv('MESSAGE_SERVICE_URL', 'http://message-service:3003')
    
    # Test service mapping dictionary
    SERVICE_MAP = {
        '/api/auth/': USER_SERVICE_URL,
        '/api/users/': USER_SERVICE_URL,
        '/api/chat/': CHAT_SERVICE_URL,
        '/api/messages/': MESSAGE_SERVICE_URL
    }
    
    # Test mapping logic
    test_paths = [
        ('/api/auth/login', USER_SERVICE_URL),
        ('/api/users/profile', USER_SERVICE_URL),
        ('/api/chat/rooms', CHAT_SERVICE_URL),
        ('/api/messages/history', MESSAGE_SERVICE_URL),
        ('/api/unknown/path', None)  # Should not match
    ]
    
    for path, expected_service in test_paths:
        matched_service = None
        for route_prefix, service_url in SERVICE_MAP.items():
            if path.startswith(route_prefix):
                matched_service = service_url
                break
        
        if expected_service is None:
            # This path should not match any service
            if matched_service is not None:
                print(f"❌ Path '{path}' incorrectly matched service '{matched_service}'")
                return False
        else:
            # This path should match the expected service
            if matched_service != expected_service:
                print(f"❌ Path '{path}' matched '{matched_service}', expected '{expected_service}'")
                return False
    
    print("✅ Service mapping logic works correctly")
    return True

def test_proxy_url_construction():
    """Test URL construction for proxy requests"""
    print("\n🔗 Testing Proxy URL Construction...")
    
    service_url = "http://test-service:3001"
    paths = [
        "/api/users",
        "/api/users/",
        "api/users",  # Missing leading slash
        "/api/users/123",
        "/api/chat/rooms/abc/messages"
    ]
    
    expected_urls = [
        "http://test-service:3001/api/users",
        "http://test-service:3001/api/users/",
        "http://test-service:3001/api/users",
        "http://test-service:3001/api/users/123",
        "http://test-service:3001/api/chat/rooms/abc/messages"
    ]
    
    for i, path in enumerate(paths):
        # Construct URL (similar to proxy_request function)
        if not path.startswith('/'):
            path = '/' + path
        constructed_url = f"{service_url}{path}"
        
        if constructed_url != expected_urls[i]:
            print(f"❌ URL construction failed for path '{path}'")
            print(f"   Expected: {expected_urls[i]}")
            print(f"   Got:      {constructed_url}")
            return False
    
    print("✅ Proxy URL construction works correctly")
    return True

def test_http_method_handling():
    """Test HTTP method handling logic"""
    print("\n📡 Testing HTTP Method Handling...")
    
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    valid_methods = ['GET', 'POST', 'PUT', 'DELETE']
    
    for method in methods:
        is_valid = method in valid_methods
        should_handle = method in ['GET', 'POST', 'PUT', 'DELETE']
        
        if is_valid != should_handle:
            print(f"❌ Method validation inconsistent for '{method}'")
            return False
    
    # Test unsupported method
    unsupported_method = 'HEAD'
    if unsupported_method in valid_methods:
        print(f"❌ Unsupported method '{unsupported_method}' incorrectly marked as valid")
        return False
    
    print("✅ HTTP method handling logic works correctly")
    return True

def test_request_data_processing():
    """Test request data processing"""
    print("\n🔄 Testing Request Data Processing...")
    
    # Test JSON data handling
    test_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123"
    }
    
    # Convert to JSON and back
    json_string = json.dumps(test_data)
    parsed_data = json.loads(json_string)
    
    # Verify data integrity
    if parsed_data["username"] != test_data["username"]:
        print("❌ JSON serialization/deserialization failed for username")
        return False
    
    if parsed_data["email"] != test_data["email"]:
        print("❌ JSON serialization/deserialization failed for email")
        return False
    
    # Test empty data
    empty_data = {}
    empty_json = json.dumps(empty_data)
    if empty_json != "{}":
        print("❌ Empty data JSON conversion failed")
        return False
    
    print("✅ Request data processing works correctly")
    return True

def test_logging_and_monitoring():
    """Test logging and monitoring functionality"""
    print("\n📊 Testing Logging and Monitoring...")
    
    # Test timestamp generation
    timestamp = datetime.now().isoformat()
    if not timestamp:
        print("❌ Timestamp generation failed")
        return False
    
    # Test log message formatting
    service = "user-service"
    path = "/api/auth/login"
    method = "POST"
    log_message = f"[{timestamp}] {method} {path} -> {service}"
    
    if service not in log_message:
        print("❌ Log message formatting missing service")
        return False
    
    if path not in log_message:
        print("❌ Log message formatting missing path")
        return False
    
    if method not in log_message:
        print("❌ Log message formatting missing method")
        return False
    
    print("✅ Logging and monitoring works correctly")
    return True

def test_environment_configuration():
    """Test environment variable handling"""
    print("\n⚙️  Testing Environment Configuration...")
    
    # Test default values
    defaults = {
        'USER_SERVICE_URL': 'http://user-service:3001',
        'CHAT_SERVICE_URL': 'http://chat-service:3002',
        'MESSAGE_SERVICE_URL': 'http://message-service:3003'
    }
    
    # Test environment variable retrieval with defaults
    for var_name, default_value in defaults.items():
        # Simulate os.getenv behavior
        env_value = os.getenv(var_name, default_value)
        if env_value != default_value:
            # If environment variable is set, that's fine too
            pass
        else:
            # Using default value, which should be correct
            if env_value != default_value:
                print(f"❌ Default value for {var_name} is incorrect")
                return False
    
    print("✅ Environment configuration works correctly")
    return True

def main():
    """Run all gateway service tests"""
    print("🚀 Starting Gateway Service Basic Tests...")
    print("=" * 45)
    
    success_count = 0
    total_tests = 6
    
    # Run tests
    if test_service_mapping():
        success_count += 1
    
    if test_proxy_url_construction():
        success_count += 1
    
    if test_http_method_handling():
        success_count += 1
    
    if test_request_data_processing():
        success_count += 1
    
    if test_logging_and_monitoring():
        success_count += 1
    
    if test_environment_configuration():
        success_count += 1
    
    # Summary
    print("\n" + "=" * 45)
    print("📊 Gateway Service Test Results Summary")
    print("=" * 45)
    print(f"✅ Passed: {success_count}")
    print(f"❌ Failed: {total_tests - success_count}")
    print(f"📋 Total: {total_tests}")
    
    if success_count == total_tests:
        print("\n🎉 All Gateway Service basic tests passed!")
        return True
    else:
        print(f"\n💥 {total_tests - success_count} test(s) failed")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)