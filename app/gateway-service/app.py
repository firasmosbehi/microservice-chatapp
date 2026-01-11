from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://user-service:3001')
CHAT_SERVICE_URL = os.getenv('CHAT_SERVICE_URL', 'http://chat-service:3002')
MESSAGE_SERVICE_URL = os.getenv('MESSAGE_SERVICE_URL', 'http://message-service:3003')

# Service mapping
SERVICE_MAP = {
    '/api/auth/': USER_SERVICE_URL,
    '/api/users/': USER_SERVICE_URL,
    '/api/chat/': CHAT_SERVICE_URL,
    '/api/messages/': MESSAGE_SERVICE_URL
}

def proxy_request(service_url, path, method, data=None):
    """Proxy request to the appropriate service"""
    url = f"{service_url}{path}"
    logger.info(f"Proxying {method} request to: {url}")
    
    try:
        if method == 'GET':
            response = requests.get(url, timeout=30)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=30)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=30)
        elif method == 'DELETE':
            response = requests.delete(url, timeout=30)
        else:
            return jsonify({'error': 'Method not allowed'}), 405
        
        # Return the response from the service
        try:
            return jsonify(response.json()), response.status_code
        except:
            return response.text, response.status_code
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Proxy request failed: {e}")
        return jsonify({
            'error': 'Service temporarily unavailable',
            'details': str(e)
        }), 503

@app.route('/')
def index():
    return jsonify({
        'message': 'Gateway Service Running',
        'version': '1.0.0',
        'description': 'API Gateway for Chat Application Microservices',
        'endpoints': {
            'health': '/health',
            'auth': '/api/auth/*',
            'users': '/api/users/*',
            'chat': '/api/chat/*',
            'messages': '/api/messages/*'
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint that checks all services"""
    services = []
    
    # Check user service
    user_status = check_service_health(USER_SERVICE_URL, "User Service")
    services.append(user_status)
    
    # Check chat service
    chat_status = check_service_health(CHAT_SERVICE_URL, "Chat Service")
    services.append(chat_status)
    
    # Check message service
    message_status = check_service_health(MESSAGE_SERVICE_URL, "Message Service")
    services.append(message_status)
    
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'services': services,
        'timestamp': datetime.utcnow().isoformat()
    })

def check_service_health(url, name):
    """Check if a service is healthy"""
    try:
        response = requests.get(f"{url}/", timeout=5)
        status = 'healthy' if response.status_code == 200 else 'unhealthy'
    except:
        status = 'unhealthy'
    
    return {
        'name': name,
        'url': url,
        'status': status,
        'last_checked': datetime.utcnow().isoformat()
    }

# Auth routes
@app.route('/api/auth/<path:endpoint>', methods=['POST'])
def auth_routes(endpoint):
    path = f"/{endpoint}"
    return proxy_request(USER_SERVICE_URL, path, 'POST', request.get_json())

# User routes
@app.route('/api/users/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user_routes(endpoint):
    path = f"/{endpoint}"
    return proxy_request(USER_SERVICE_URL, path, request.method, request.get_json())

# Chat routes
@app.route('/api/chat/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def chat_routes(endpoint):
    path = f"/{endpoint}"
    # Only pass JSON data for POST, PUT requests
    data = request.get_json() if request.method in ['POST', 'PUT'] else None
    return proxy_request(CHAT_SERVICE_URL, path, request.method, data)

# Message routes
@app.route('/api/messages/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def message_routes(endpoint):
    path = f"/{endpoint}"
    # Only pass JSON data for POST, PUT requests
    data = request.get_json() if request.method in ['POST', 'PUT'] else None
    return proxy_request(MESSAGE_SERVICE_URL, path, request.method, data)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    logger.info(f"Starting Gateway Service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)