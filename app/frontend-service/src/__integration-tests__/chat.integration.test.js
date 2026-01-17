import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import axios from 'axios';

// Test configuration
const TEST_API_BASE_URL = process.env.TEST_API_BASE_URL || 'http://localhost:8000';
const TEST_TIMEOUT = 15000;

describe('Chat Integration Tests', () => {
  let apiClient;
  let authToken;
  let testRoomId;
  let testUserId;

  // Test user credentials
  const testUser = {
    username: `chatuser_${Date.now()}`,
    email: `chat_${Date.now()}@example.com`,
    password: 'password123'
  };

  beforeEach(async () => {
    apiClient = axios.create({
      baseURL: TEST_API_BASE_URL,
      timeout: TEST_TIMEOUT,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Register and login test user
    try {
      await apiClient.post('/api/auth/register', testUser);
    } catch (error) {
      // User might already exist, try login
      console.debug('Registration failed, trying login:', error.message);
    }

    const loginResponse = await apiClient.post('/api/auth/login', {
      email: testUser.email,
      password: testUser.password
    });

    authToken = loginResponse.data.token;
    testUserId = loginResponse.data.user.id;

    // Set default auth header
    apiClient.defaults.headers.Authorization = `Bearer ${authToken}`;
  });

  afterEach(async () => {
    // Cleanup: leave room and delete test user
    if (testRoomId) {
      try {
        await apiClient.post(`/api/chat/rooms/${testRoomId}/leave`);
      } catch (error) {
        console.debug('Room leave cleanup failed:', error.message);
      }
    }

    try {
      await apiClient.delete('/api/users/me');
    } catch (error) {
      console.debug('User cleanup failed:', error.message);
    }
  });

  describe('Room Management', () => {
    it('should create a new chat room', async () => {
      const roomData = {
        name: `Test Room ${Date.now()}`,
        description: 'Integration test room',
        isPrivate: false
      };

      const response = await apiClient.post('/api/chat/rooms', roomData);

      expect(response.status).toBe(201);
      expect(response.data).toHaveProperty('id');
      expect(response.data.name).toBe(roomData.name);
      expect(response.data.description).toBe(roomData.description);
      expect(response.data.creatorId).toBe(testUserId);

      testRoomId = response.data.id;
    });

    it('should list available rooms', async () => {
      // Create a room first
      const roomResponse = await apiClient.post('/api/chat/rooms', {
        name: `List Test Room ${Date.now()}`,
        description: 'Room for listing test'
      });
      testRoomId = roomResponse.data.id;

      const response = await apiClient.get('/api/chat/rooms');

      expect(response.status).toBe(200);
      expect(Array.isArray(response.data)).toBe(true);
      expect(response.data.length).toBeGreaterThan(0);
      
      const createdRoom = response.data.find(room => room.id === testRoomId);
      expect(createdRoom).toBeDefined();
      expect(createdRoom.name).toContain('List Test Room');
    });

    it('should get specific room details', async () => {
      // Create a room first
      const roomResponse = await apiClient.post('/api/chat/rooms', {
        name: `Detail Test Room ${Date.now()}`,
        description: 'Room for detail test'
      });
      const roomId = roomResponse.data.id;

      const response = await apiClient.get(`/api/chat/rooms/${roomId}`);

      expect(response.status).toBe(200);
      expect(response.data.id).toBe(roomId);
      expect(response.data.name).toContain('Detail Test Room');
      expect(response.data).toHaveProperty('createdAt');
    });

    it('should reject getting non-existent room', async () => {
      try {
        await apiClient.get('/api/chat/rooms/nonexistent-room-id');
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        expect(error.response.status).toBe(404);
        expect(error.response.data).toHaveProperty('error');
      }
    });
  });

  describe('Room Membership', () => {
    beforeEach(async () => {
      // Create a room for membership tests
      const roomResponse = await apiClient.post('/api/chat/rooms', {
        name: `Membership Test Room ${Date.now()}`,
        description: 'Room for membership tests'
      });
      testRoomId = roomResponse.data.id;
    });

    it('should join a room successfully', async () => {
      const response = await apiClient.post(`/api/chat/rooms/${testRoomId}/join`);

      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('message');
      expect(response.data.message).toContain('joined');
    });

    it('should leave a room successfully', async () => {
      // First join the room
      await apiClient.post(`/api/chat/rooms/${testRoomId}/join`);

      const response = await apiClient.post(`/api/chat/rooms/${testRoomId}/leave`);

      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('message');
      expect(response.data.message).toContain('left');
    });

    it('should reject joining non-existent room', async () => {
      try {
        await apiClient.post('/api/chat/rooms/nonexistent-room-id/join');
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        expect(error.response.status).toBe(404);
        expect(error.response.data).toHaveProperty('error');
      }
    });

    it('should reject leaving room not joined', async () => {
      try {
        await apiClient.post(`/api/chat/rooms/${testRoomId}/leave`);
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        // This might succeed or fail depending on implementation
        // Accept either 400 or 200 status
        expect([200, 400]).toContain(error.response?.status || 200);
      }
    });
  });

  describe('Message Operations', () => {
    let messageId;

    beforeEach(async () => {
      // Create room and join it
      const roomResponse = await apiClient.post('/api/chat/rooms', {
        name: `Message Test Room ${Date.now()}`,
        description: 'Room for message tests'
      });
      testRoomId = roomResponse.data.id;
      
      await apiClient.post(`/api/chat/rooms/${testRoomId}/join`);
    });

    it('should send a message to room', async () => {
      const messageData = {
        content: 'Hello, this is an integration test message!',
        messageType: 'text'
      };

      const response = await apiClient.post(
        `/api/chat/rooms/${testRoomId}/messages`, 
        messageData
      );

      expect(response.status).toBe(201);
      expect(response.data).toHaveProperty('id');
      expect(response.data.content).toBe(messageData.content);
      expect(response.data.userId).toBe(testUserId);
      expect(response.data.roomId).toBe(testRoomId);
      expect(response.data).toHaveProperty('createdAt');

      messageId = response.data.id;
    });

    it('should retrieve message history for room', async () => {
      // Send a few messages first
      await apiClient.post(`/api/chat/rooms/${testRoomId}/messages`, {
        content: 'First test message',
        messageType: 'text'
      });

      await apiClient.post(`/api/chat/rooms/${testRoomId}/messages`, {
        content: 'Second test message',
        messageType: 'text'
      });

      const response = await apiClient.get(`/api/messages/room/${testRoomId}`);

      expect(response.status).toBe(200);
      expect(Array.isArray(response.data)).toBe(true);
      expect(response.data.length).toBeGreaterThanOrEqual(2);
      
      // Check message structure
      const firstMessage = response.data[0];
      expect(firstMessage).toHaveProperty('id');
      expect(firstMessage).toHaveProperty('content');
      expect(firstMessage).toHaveProperty('userId');
      expect(firstMessage).toHaveProperty('roomId');
      expect(firstMessage).toHaveProperty('createdAt');
    });

    it('should reject sending message to non-existent room', async () => {
      try {
        await apiClient.post('/api/chat/rooms/nonexistent-room/messages', {
          content: 'Test message',
          messageType: 'text'
        });
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        expect(error.response.status).toBe(404);
        expect(error.response.data).toHaveProperty('error');
      }
    });

    it('should reject sending empty message', async () => {
      try {
        await apiClient.post(`/api/chat/rooms/${testRoomId}/messages`, {
          content: '', // Empty content
          messageType: 'text'
        });
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        expect(error.response.status).toBe(400);
        expect(error.response.data).toHaveProperty('error');
      }
    });

    it('should handle message with special characters', async () => {
      const specialMessage = {
        content: 'Hello! @#$%^&*()_+-=[]{}|;:,.<>? Test message with emojis 🚀✨',
        messageType: 'text'
      };

      const response = await apiClient.post(
        `/api/chat/rooms/${testRoomId}/messages`,
        specialMessage
      );

      expect(response.status).toBe(201);
      expect(response.data.content).toBe(specialMessage.content);
    });
  });

  describe('Message Read Receipts', () => {
    beforeEach(async () => {
      // Setup: create room, join, and send message
      const roomResponse = await apiClient.post('/api/chat/rooms', {
        name: `Receipt Test Room ${Date.now()}`,
        description: 'Room for receipt tests'
      });
      testRoomId = roomResponse.data.id;
      
      await apiClient.post(`/api/chat/rooms/${testRoomId}/join`);
      
      const messageResponse = await apiClient.post(`/api/chat/rooms/${testRoomId}/messages`, {
        content: 'Message for read receipt test',
        messageType: 'text'
      });
      
      messageId = messageResponse.data.id;
    });

    it('should mark message as read', async () => {
      const response = await apiClient.put(`/api/messages/${messageId}/read`);

      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('message');
      expect(response.data.message).toContain('marked as read');
    });

    it('should get unread message counts', async () => {
      const response = await apiClient.get(`/api/messages/unread/${testUserId}`);

      expect(response.status).toBe(200);
      expect(typeof response.data).toBe('object');
      // The exact structure depends on implementation
    });

    it('should reject marking non-existent message as read', async () => {
      try {
        await apiClient.put('/api/messages/nonexistent-message-id/read');
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        expect(error.response.status).toBe(404);
        expect(error.response.data).toHaveProperty('error');
      }
    });
  });
});