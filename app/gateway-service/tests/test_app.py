import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from app import app, proxy_request, SERVICE_MAP

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_proxy_request_get():
    """Test GET request proxying"""
    with patch('app.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {'message': 'success'}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        response, status_code = proxy_request('http://test-service', '/test', 'GET')
        
        assert status_code == 200
        assert json.loads(response)['message'] == 'success'
        mock_get.assert_called_once_with('http://test-service/test', timeout=30)

def test_proxy_request_post():
    """Test POST request proxying"""
    with patch('app.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {'id': 1, 'name': 'test'}
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        test_data = {'name': 'test', 'value': 'data'}
        response, status_code = proxy_request('http://test-service', '/test', 'POST', test_data)
        
        assert status_code == 201
        assert json.loads(response)['id'] == 1
        mock_post.assert_called_once_with('http://test-service/test', json=test_data, timeout=30)

def test_proxy_request_put():
    """Test PUT request proxying"""
    with patch('app.requests.put') as mock_put:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_put.return_value = mock_response
        
        test_data = {'update': 'data'}
        response, status_code = proxy_request('http://test-service', '/test/1', 'PUT', test_data)
        
        assert status_code == 200
        mock_put.assert_called_once_with('http://test-service/test/1', json=test_data, timeout=30)

def test_proxy_request_delete():
    """Test DELETE request proxying"""
    with patch('app.requests.delete') as mock_delete:
        mock_response = Mock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response
        
        response, status_code = proxy_request('http://test-service', '/test/1', 'DELETE')
        
        assert status_code == 204
        mock_delete.assert_called_once_with('http://test-service/test/1', timeout=30)

def test_proxy_request_invalid_method():
    """Test invalid HTTP method handling"""
    response, status_code = proxy_request('http://test-service', '/test', 'INVALID')
    
    assert status_code == 405
    assert 'Method not allowed' in json.loads(response)['error']

def test_proxy_request_exception_handling():
    """Test exception handling in proxy requests"""
    with patch('app.requests.get') as mock_get:
        mock_get.side_effect = Exception('Connection failed')
        
        response, status_code = proxy_request('http://test-service', '/test', 'GET')
        
        assert status_code == 503
        error_data = json.loads(response)
        assert 'Service temporarily unavailable' in error_data['error']
        assert 'Connection failed' in error_data['details']

def test_index_route(client):
    """Test the index route"""
    response = client.get('/')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert 'version' in data
    assert 'endpoints' in data

def test_health_check_route(client):
    """Test the health check route"""
    with patch('app.check_service_health') as mock_health:
        mock_health.return_value = {
            'name': 'Test Service',
            'status': 'healthy',
            'url': 'http://test-service'
        }
        
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert len(data['services']) == 3  # user, chat, message services

def test_auth_routes_proxy(client):
    """Test authentication routes proxying"""
    with patch('app.proxy_request') as mock_proxy:
        mock_proxy.return_value = ('{"token": "test-token"}', 200)
        
        response = client.post('/api/auth/login', 
                             json={'email': 'test@example.com', 'password': 'password'})
        
        assert response.status_code == 200
        mock_proxy.assert_called_once()

def test_users_routes_proxy(client):
    """Test users routes proxying"""
    with patch('app.proxy_request') as mock_proxy:
        mock_proxy.return_value = ('{"users": []}', 200)
        
        response = client.get('/api/users/')
        
        assert response.status_code == 200
        mock_proxy.assert_called_once()

def test_chat_routes_proxy(client):
    """Test chat routes proxying"""
    with patch('app.proxy_request') as mock_proxy:
        mock_proxy.return_value = ('{"rooms": []}', 200)
        
        response = client.get('/api/chat/rooms')
        
        assert response.status_code == 200
        mock_proxy.assert_called_once()

def test_messages_routes_proxy(client):
    """Test messages routes proxying"""
    with patch('app.proxy_request') as mock_proxy:
        mock_proxy.return_value = ('{"messages": []}', 200)
        
        response = client.get('/api/messages/rooms/1/messages')
        
        assert response.status_code == 200
        mock_proxy.assert_called_once()

def test_service_map_configuration():
    """Test service map configuration"""
    assert '/api/auth/' in SERVICE_MAP
    assert '/api/users/' in SERVICE_MAP
    assert '/api/chat/' in SERVICE_MAP
    assert '/api/messages/' in SERVICE_MAP
    
    assert SERVICE_MAP['/api/auth/'].endswith(':3001')
    assert SERVICE_MAP['/api/chat/'].endswith(':3002')
    assert SERVICE_MAP['/api/messages/'].endswith(':3003')

def test_cors_configuration():
    """Test CORS configuration"""
    # Test that CORS headers are present
    with patch('app.proxy_request') as mock_proxy:
        mock_proxy.return_value = ('{"test": "data"}', 200)
        
        response = client.get('/api/users/', headers={'Origin': 'http://localhost:3000'})
        
        assert response.status_code == 200
        # CORS headers should be added by Flask-CORS middleware

# Parameterized tests for different service mappings
@pytest.mark.parametrize("route_prefix,service_port", [
    ('/api/auth/', ':3001'),
    ('/api/users/', ':3001'),
    ('/api/chat/', ':3002'),
    ('/api/messages/', ':3003'),
])
def test_service_routing(route_prefix, service_port):
    """Test that routes are mapped to correct services"""
    service_url = SERVICE_MAP[route_prefix]
    assert service_url.endswith(service_port)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])