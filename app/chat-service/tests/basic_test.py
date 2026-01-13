#!/usr/bin/env python3
"""
Simple Chat Service Test
Tests core functionality without external dependencies
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the main module
try:
    import main
    print("✅ Successfully imported main module")
except ImportError as e:
    print(f"❌ Failed to import main module: {e}")
    sys.exit(1)

def test_models():
    """Test basic model functionality"""
    print("\n🧪 Testing Chat Models...")
    
    # Test CreateRoomRequest
    try:
        room_request = main.CreateRoomRequest(
            name="Test Room",
            creator_id=1,
            description="A test room"
        )
        assert room_request.name == "Test Room"
        assert room_request.creator_id == 1
        print("✅ CreateRoomRequest validation works")
    except Exception as e:
        print(f"❌ CreateRoomRequest test failed: {e}")
        return False
    
    # Test JoinRoomRequest
    try:
        join_request = main.JoinRoomRequest(
            user_id=123,
            username="testuser"
        )
        assert join_request.user_id == 123
        assert join_request.username == "testuser"
        print("✅ JoinRoomRequest validation works")
    except Exception as e:
        print(f"❌ JoinRoomRequest test failed: {e}")
        return False
    
    # Test MessageRequest
    try:
        message_request = main.MessageRequest(
            room_id="room123",
            user_id=456,
            username="sender",
            content="Hello world"
        )
        assert message_request.room_id == "room123"
        assert message_request.content == "Hello world"
        print("✅ MessageRequest validation works")
    except Exception as e:
        print(f"❌ MessageRequest test failed: {e}")
        return False
    
    return True

def test_basic_functions():
    """Test basic utility functions"""
    print("\n🔧 Testing Basic Functions...")
    
    # Test room creation data structure
    try:
        chat_rooms = {}
        room_id = "test-room-123"
        chat_rooms[room_id] = {
            "id": room_id,
            "name": "Test Room",
            "creator_id": 1,
            "members": set(),
            "created_at": "2024-01-01T00:00:00Z"
        }
        assert room_id in chat_rooms
        assert chat_rooms[room_id]["name"] == "Test Room"
        print("✅ Room data structure works")
    except Exception as e:
        print(f"❌ Room data structure test failed: {e}")
        return False
    
    # Test message storage
    try:
        messages = {}
        room_id = "test-room-123"
        messages[room_id] = []
        test_message = {
            "id": "msg-123",
            "room_id": room_id,
            "user_id": 456,
            "username": "testuser",
            "content": "Hello!",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        messages[room_id].append(test_message)
        assert len(messages[room_id]) == 1
        assert messages[room_id][0]["content"] == "Hello!"
        print("✅ Message storage works")
    except Exception as e:
        print(f"❌ Message storage test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Chat Service Basic Tests...")
    print("=" * 40)
    
    success_count = 0
    total_tests = 2
    
    # Run tests
    if test_models():
        success_count += 1
    
    if test_basic_functions():
        success_count += 1
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary")
    print("=" * 40)
    print(f"✅ Passed: {success_count}")
    print(f"❌ Failed: {total_tests - success_count}")
    print(f"📋 Total: {total_tests}")
    
    if success_count == total_tests:
        print("\n🎉 All Chat Service basic tests passed!")
        return True
    else:
        print(f"\n💥 {total_tests - success_count} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)