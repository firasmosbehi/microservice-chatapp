#!/usr/bin/env python3
"""
Chat Service Test Script
Demonstrates the full functionality of the chat service
"""

import requests
import json
import time

BASE_URL = "http://localhost:3002"

def test_chat_service():
    print("=== Chat Service Functional Test ===\n")
    
    # Test 1: Service Health Check
    print("1. Testing service health...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Response: {response.json()}\n")
    
    # Test 2: Create Chat Room
    print("2. Creating chat room...")
    room_data = {
        "name": "Test Room",
        "creator_id": 1,
        "description": "Testing room functionality"
    }
    response = requests.post(f"{BASE_URL}/rooms", json=room_data)
    room = response.json()
    room_id = room["id"]
    print(f"   Created room: {room['name']} (ID: {room_id})\n")
    
    # Test 3: List All Rooms
    print("3. Listing all rooms...")
    response = requests.get(f"{BASE_URL}/rooms")
    rooms = response.json()
    print(f"   Total rooms: {len(rooms)}")
    for r in rooms:
        print(f"   - {r['name']} ({r['member_count']} members)")
    print()
    
    # Test 4: Join Room
    print("4. Joining room as Alice...")
    join_data = {"user_id": 2, "username": "Alice"}
    response = requests.post(f"{BASE_URL}/rooms/{room_id}/join", json=join_data)
    result = response.json()
    print(f"   Join result: {result['message']}")
    print(f"   Members now: {result['room']['member_count']}\n")
    
    # Test 5: Send Message
    print("5. Sending message...")
    message_data = {
        "room_id": room_id,
        "user_id": 2,
        "username": "Alice",
        "content": "Hello from the test script!"
    }
    response = requests.post(f"{BASE_URL}/messages", json=message_data)
    result = response.json()
    print(f"   Message sent: {result['message']}\n")
    
    # Test 6: Retrieve Messages
    print("6. Retrieving messages...")
    response = requests.get(f"{BASE_URL}/rooms/{room_id}/messages")
    messages = response.json()
    print(f"   Retrieved {len(messages)} messages:")
    for msg in reversed(messages):  # Show in chronological order
        timestamp = msg['timestamp'].split('T')[1][:8]  # Just time part
        print(f"   [{timestamp}] {msg['username']}: {msg['content']}")
    print()
    
    # Test 7: Leave Room
    print("7. Leaving room...")
    response = requests.post(f"{BASE_URL}/rooms/{room_id}/leave", json=join_data)
    result = response.json()
    print(f"   Leave result: {result['message']}\n")
    
    print("=== All tests completed successfully! ===")

if __name__ == "__main__":
    test_chat_service()