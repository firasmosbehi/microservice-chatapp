#!/bin/bash

echo "=== Message Service Functional Test ==="
echo

BASE_URL="http://localhost:3003"

# Test 1: Health Check
echo "1. Testing service health..."
curl -s $BASE_URL/ | jq .
echo

# Test 2: Create Room
echo "2. Creating chat room..."
ROOM_RESPONSE=$(curl -s -X POST $BASE_URL/rooms \
  -H "Content-Type: application/json" \
  -d '{"name": "General Discussion", "description": "Main chat room", "created_by": 1}')

echo $ROOM_RESPONSE | jq .
ROOM_ID=$(echo $ROOM_RESPONSE | jq -r '.id')
echo "Created room ID: $ROOM_ID"
echo

# Test 3: Get All Rooms
echo "3. Getting all rooms..."
curl -s $BASE_URL/rooms | jq .
echo

# Test 4: Send Message
echo "4. Sending message to room..."
MESSAGE_RESPONSE=$(curl -s -X POST $BASE_URL/messages \
  -H "Content-Type: application/json" \
  -d "{\"room_id\": $ROOM_ID, \"sender_id\": 1, \"content\": \"Hello everyone! This is my first message.\", \"message_type\": \"text\"}")

echo $MESSAGE_RESPONSE | jq .
MESSAGE_ID=$(echo $MESSAGE_RESPONSE | jq -r '.id')
echo "Sent message ID: $MESSAGE_ID"
echo

# Test 5: Send Another Message
echo "5. Sending another message..."
curl -s -X POST $BASE_URL/messages \
  -H "Content-Type: application/json" \
  -d "{\"room_id\": $ROOM_ID, \"sender_id\": 2, \"content\": \"Hi there! Welcome to the chat.\", \"message_type\": \"text\"}" | jq .
echo

# Test 6: Get Room Messages
echo "6. Getting messages from room..."
curl -s "$BASE_URL/rooms/$ROOM_ID/messages" | jq .
echo

# Test 7: Get Specific Message
echo "7. Getting specific message..."
curl -s "$BASE_URL/messages/$MESSAGE_ID" | jq .
echo

# Test 8: Mark Message as Read
echo "8. Marking message as read..."
curl -s -X POST $BASE_URL/receipts \
  -H "Content-Type: application/json" \
  -d "{\"message_id\": $MESSAGE_ID, \"user_id\": 2}" | jq .
echo

# Test 9: Get Read Receipts
echo "9. Getting read receipts..."
curl -s "$BASE_URL/messages/$MESSAGE_ID/receipts" | jq .
echo

# Test 10: Search Messages
echo "10. Searching messages..."
curl -s "$BASE_URL/search?q=hello" | jq .
echo

# Test 11: Delete Message
echo "11. Deleting message..."
curl -s -X DELETE "$BASE_URL/messages/$MESSAGE_ID" | jq .
echo

# Test 12: Verify Deletion
echo "12. Verifying message deletion..."
curl -s "$BASE_URL/messages/$MESSAGE_ID" | jq .
echo

echo "=== All tests completed! ==="