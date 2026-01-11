#!/bin/bash

echo "=== User Service Full Functionality Test ==="
echo

BASE_URL="http://localhost:3001"

# Test 1: Health Check
echo "1. Testing service health..."
curl -s $BASE_URL/ | jq .
echo

# Test 2: User Registration
echo "2. Registering new user..."
REGISTER_RESPONSE=$(curl -s -X POST $BASE_URL/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice_wonder", "email": "alice@test.com", "password": "wonderland123", "firstName": "Alice", "lastName": "Wonder"}')

echo $REGISTER_RESPONSE | jq .
echo

# Extract tokens from registration response
ACCESS_TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.tokens.accessToken')
REFRESH_TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.tokens.refreshToken')
USER_ID=$(echo $REGISTER_RESPONSE | jq -r '.user.id')

echo "Extracted tokens:"
echo "Access Token: $ACCESS_TOKEN"
echo "Refresh Token: $REFRESH_TOKEN"
echo

# Test 3: User Login
echo "3. Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@test.com", "password": "wonderland123"}')

echo $LOGIN_RESPONSE | jq .
echo

# Test 4: Profile Access
echo "4. Accessing user profile..."
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" $BASE_URL/profile | jq .
echo

# Test 5: Profile Update
echo "5. Updating user profile..."
UPDATE_RESPONSE=$(curl -s -X PUT $BASE_URL/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{"firstName": "Alice", "lastName": "Updated-Wonder", "avatar": "https://example.com/avatar.jpg"}')

echo $UPDATE_RESPONSE | jq .
echo

# Test 6: Password Change
echo "6. Changing password..."
curl -s -X PUT $BASE_URL/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{"currentPassword": "wonderland123", "newPassword": "newwonderland456"}' | jq .
echo

# Test 7: Token Refresh
echo "7. Refreshing access token..."
curl -s -X POST $BASE_URL/refresh-token \
  -H "Content-Type: application/json" \
  -d "{\"refreshToken\": \"$REFRESH_TOKEN\"}" | jq .
echo

# Test 8: Get All Users (Admin)
echo "8. Getting all users..."
curl -s $BASE_URL/users | jq .
echo

# Test 9: Forgot Password
echo "9. Testing forgot password..."
curl -s -X POST $BASE_URL/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@test.com"}' | jq .
echo

# Test 10: Logout
echo "10. Testing logout..."
curl -s -X POST $BASE_URL/logout \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq .
echo

echo "=== All tests completed! ==="