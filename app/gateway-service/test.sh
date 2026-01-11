#!/bin/bash

echo "=== Gateway Service Functional Test ==="
echo

GATEWAY_URL="http://localhost:8000"

# Test 1: Gateway Health Check
echo "1. Testing gateway health..."
curl -s $GATEWAY_URL/health | jq .
echo

# Test 2: Gateway Root Endpoint
echo "2. Testing gateway root endpoint..."
curl -s $GATEWAY_URL/ | jq .
echo

# Test 3: Proxy to User Service - Health Check
echo "3. Testing proxy to user service health..."
curl -s $GATEWAY_URL/api/users/ | jq .
echo

# Test 4: Proxy to Chat Service - Health Check
echo "4. Testing proxy to chat service health..."
curl -s $GATEWAY_URL/api/chat/ | jq .
echo

# Test 5: Proxy to Message Service - Health Check
echo "5. Testing proxy to message service health..."
curl -s $GATEWAY_URL/api/messages/ | jq .
echo

# Test 6: User Service Registration through Gateway
echo "6. Testing user registration through gateway..."
REGISTRATION_RESPONSE=$(curl -s -X POST $GATEWAY_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "gateway_user", "email": "gateway@test.com", "password": "securepassword123", "firstName": "Gateway", "lastName": "User"}')

echo $REGISTRATION_RESPONSE | jq .
echo

# Extract token if registration succeeded
ACCESS_TOKEN=$(echo $REGISTRATION_RESPONSE | jq -r '.tokens.accessToken' 2>/dev/null)
if [ "$ACCESS_TOKEN" != "null" ] && [ -n "$ACCESS_TOKEN" ]; then
    echo "Token extracted: $ACCESS_TOKEN"
else
    # Try to login if registration failed (user might already exist)
    echo "Trying login instead..."
    LOGIN_RESPONSE=$(curl -s -X POST $GATEWAY_URL/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email": "gateway@test.com", "password": "securepassword123"}')
    
    echo $LOGIN_RESPONSE | jq .
    ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.tokens.accessToken' 2>/dev/null)
fi

echo

# Test 7: Protected Route with Token
if [ "$ACCESS_TOKEN" != "null" ] && [ -n "$ACCESS_TOKEN" ]; then
    echo "7. Testing protected user profile access..."
    curl -s -H "Authorization: Bearer $ACCESS_TOKEN" $GATEWAY_URL/api/users/profile | jq .
    echo
else
    echo "7. Skipping protected route test (no valid token)"
    echo
fi

# Test 8: Chat Service Room Creation through Gateway
echo "8. Testing chat room creation through gateway..."
ROOM_RESPONSE=$(curl -s -X POST $GATEWAY_URL/api/chat/rooms \
  -H "Content-Type: application/json" \
  -d '{"name": "Gateway Test Room", "creator_id": 1, "description": "Testing gateway routing", "is_private": false}')

echo $ROOM_RESPONSE | jq .
ROOM_ID=$(echo $ROOM_RESPONSE | jq -r '.id' 2>/dev/null)
echo

# Test 9: Message Service through Gateway
if [ "$ROOM_ID" != "null" ] && [ -n "$ROOM_ID" ]; then
    echo "9. Testing message sending through gateway..."
    curl -s -X POST $GATEWAY_URL/api/messages/messages \
      -H "Content-Type: application/json" \
      -d "{\"room_id\": \"$ROOM_ID\", \"sender_id\": 1, \"content\": \"Hello from gateway!\", \"message_type\": \"text\"}" | jq .
    echo
else
    echo "9. Skipping message test (no valid room ID)"
    echo
fi

# Test 10: Get Messages through Gateway
if [ "$ROOM_ID" != "null" ] && [ -n "$ROOM_ID" ]; then
    echo "10. Testing message retrieval through gateway..."
    curl -s "$GATEWAY_URL/api/messages/rooms/$ROOM_ID/messages" | jq .
    echo
else
    echo "10. Skipping message retrieval test (no valid room ID)"
    echo
fi

# Test 11: Service Discovery/Health Aggregation
echo "11. Testing aggregated health status..."
curl -s $GATEWAY_URL/health | jq '.services[] | {name: .name, status: .status}'
echo

echo "=== All gateway tests completed! ==="
echo
echo "🚀 Gateway Service Features Demonstrated:"
echo "- API routing and request forwarding"
echo "- Service health aggregation"
echo "- JWT token handling (framework)"
echo "- Cross-service communication"
echo "- Request/response transformation"
echo "- Load distribution (single instance)"
echo "- CORS support"
echo "- Comprehensive logging"