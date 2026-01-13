#!/usr/bin/env python3
"""
Chat Service Structure Test
Tests basic Python functionality and data structures
"""

import sys
import uuid
from datetime import datetime

def test_data_structures():
    """Test basic data structures used in chat service"""
    print("🧪 Testing Chat Service Data Structures...")
    
    # Test room data structure
    try:
        # Simulate chat room structure
        room = {
            "id": "room-123",
            "name": "Test Room",
            "creator_id": 1,
            "description": "A test chat room",
            "is_private": False,
            "members": set(),  # Using set for unique members
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        # Test basic operations
        room["members"].add("user-1")
        room["members"].add("user-2")
        room["members"].add("user-1")  # Duplicate should not be added
        
        assert len(room["members"]) == 2
        assert "user-1" in room["members"]
        assert room["name"] == "Test Room"
        print("✅ Room data structure works correctly")
    except Exception as e:
        print(f"❌ Room data structure test failed: {e}")
        return False
    
    # Test message data structure
    try:
        messages = []  # List to store messages chronologically
        
        # Add test messages
        msg1 = {
            "id": "msg-1",
            "room_id": "room-123",
            "user_id": 1,
            "username": "alice",
            "content": "Hello everyone!",
            "timestamp": "2024-01-01T10:00:00Z",
            "message_type": "text"
        }
        
        msg2 = {
            "id": "msg-2", 
            "room_id": "room-123",
            "user_id": 2,
            "username": "bob",
            "content": "Hi Alice!",
            "timestamp": "2024-01-01T10:01:00Z",
            "message_type": "text"
        }
        
        messages.append(msg1)
        messages.append(msg2)
        
        # Test message operations
        assert len(messages) == 2
        assert messages[0]["username"] == "alice"
        assert messages[1]["username"] == "bob"
        assert messages[1]["timestamp"] > messages[0]["timestamp"]
        print("✅ Message data structure works correctly")
    except Exception as e:
        print(f"❌ Message data structure test failed: {e}")
        return False
    
    # Test user presence tracking
    try:
        # Track users present in different rooms
        user_presence = {
            "room-123": {"alice", "bob", "charlie"},
            "room-456": {"dave", "eve"}
        }
        
        # Test presence operations
        assert "alice" in user_presence["room-123"]
        assert "dave" not in user_presence["room-123"]
        assert len(user_presence["room-123"]) == 3
        
        # Add user to room
        user_presence["room-123"].add("dave")
        assert "dave" in user_presence["room-123"]
        assert len(user_presence["room-123"]) == 4
        print("✅ User presence tracking works correctly")
    except Exception as e:
        print(f"❌ User presence tracking test failed: {e}")
        return False
    
    return True

def test_validation_logic():
    """Test basic validation logic"""
    print("\n🔍 Testing Validation Logic...")
    
    # Test room name validation
    try:
        def validate_room_name(name):
            return name and len(name.strip()) > 0 and len(name) <= 100
        
        valid_names = ["General Chat", "Team Meeting", "a"]
        invalid_names = ["", "   ", None, "a" * 101]
        
        for name in valid_names:
            assert validate_room_name(name), f"Valid name rejected: {name}"
        
        for name in invalid_names:
            assert not validate_room_name(name), f"Invalid name accepted: {name}"
        
        print("✅ Room name validation works correctly")
    except Exception as e:
        print(f"❌ Room name validation test failed: {e}")
        return False
    
    # Test message content validation
    try:
        def validate_message_content(content):
            return content and len(content.strip()) > 0 and len(content) <= 1000
        
        valid_contents = ["Hello!", "This is a test message", "a"]
        invalid_contents = ["", "   ", None, "a" * 1001]
        
        for content in valid_contents:
            assert validate_message_content(content), f"Valid content rejected: {content}"
        
        for content in invalid_contents:
            assert not validate_message_content(content), f"Invalid content accepted: {content}"
        
        print("✅ Message content validation works correctly")
    except Exception as e:
        print(f"❌ Message content validation test failed: {e}")
        return False
    
    return True

def test_utility_functions():
    """Test basic utility functions"""
    print("\n⚙️  Testing Utility Functions...")
    
    # Test ID generation
    try:
        import uuid
        
        def generate_room_id():
            return f"room-{uuid.uuid4().hex[:8]}"
        
        def generate_message_id():
            return f"msg-{uuid.uuid4().hex[:12]}"
        
        # Generate IDs
        room_id = generate_room_id()
        msg_id = generate_message_id()
        
        # Test ID format
        assert room_id.startswith("room-")
        assert msg_id.startswith("msg-")
        assert len(room_id) == 13  # "room-" + 8 chars
        assert len(msg_id) == 16   # "msg-" + 12 chars
        
        # Test uniqueness (generate multiple)
        ids = set()
        for _ in range(100):
            new_id = generate_room_id()
            assert new_id not in ids, "Duplicate ID generated"
            ids.add(new_id)
        
        print("✅ ID generation works correctly")
    except Exception as e:
        print(f"❌ ID generation test failed: {e}")
        return False
    
    # Test timestamp handling
    try:
        from datetime import datetime
        
        def get_current_timestamp():
            return datetime.now().isoformat() + "Z"
        
        # Test timestamp format
        timestamp = get_current_timestamp()
        assert timestamp.endswith("Z")
        assert "T" in timestamp
        
        # Test timestamp parsing
        parsed_time = datetime.fromisoformat(timestamp.rstrip('Z'))
        assert isinstance(parsed_time, datetime)
        
        print("✅ Timestamp handling works correctly")
    except Exception as e:
        print(f"❌ Timestamp handling test failed: {e}")
        return False
    
    return True

def main():
    """Run all chat service tests"""
    print("🚀 Starting Chat Service Basic Tests...")
    print("=" * 45)
    
    success_count = 0
    total_tests = 3
    
    # Run tests
    if test_data_structures():
        success_count += 1
    
    if test_validation_logic():
        success_count += 1
        
    if test_utility_functions():
        success_count += 1
    
    # Summary
    print("\n" + "=" * 45)
    print("📊 Chat Service Test Results Summary")
    print("=" * 45)
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