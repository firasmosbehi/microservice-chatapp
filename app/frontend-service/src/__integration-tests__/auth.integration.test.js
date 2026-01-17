import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import axios from 'axios';

// Test configuration
// eslint-disable-next-line no-undef
const TEST_API_BASE_URL = process.env.TEST_API_BASE_URL || 'http://localhost:8000';
const TEST_TIMEOUT = 10000;

// Test user data
const testUser = {
  username: `testuser_${Date.now()}`,
  email: `test_${Date.now()}@example.com`,
  password: 'password123',
  firstName: 'Test',
  lastName: 'User'
};

describe('Authentication Integration Tests', () => {
  let apiClient;
  let registeredUserToken = null;

  beforeEach(() => {
    apiClient = axios.create({
      baseURL: TEST_API_BASE_URL,
      timeout: TEST_TIMEOUT,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  });

  afterEach(async () => {
    // Clean up: try to delete test user if token exists
    if (registeredUserToken) {
      try {
        await apiClient.delete('/api/users/me', {
          headers: { Authorization: `Bearer ${registeredUserToken}` }
        });
      } catch (error) {
        // Ignore cleanup errors
        console.debug('Cleanup failed:', error.message);
      }
      registeredUserToken = null;
    }
  });

  describe('User Registration', () => {
    it('should register a new user successfully', async () => {
      const response = await apiClient.post('/api/auth/register', {
        username: testUser.username,
        email: testUser.email,
        password: testUser.password,
        firstName: testUser.firstName,
        lastName: testUser.lastName
      });

      expect(response.status).toBe(201);
      expect(response.data).toHaveProperty('token');
      expect(response.data.user).toHaveProperty('id');
      expect(response.data.user.email).toBe(testUser.email);
      expect(response.data.user.username).toBe(testUser.username);
      
      // Store token for cleanup
      registeredUserToken = response.data.token;
    });

    it('should reject registration with invalid email', async () => {
      try {
        await apiClient.post('/api/auth/register', {
          username: 'testuser',
          email: 'invalid-email',
          password: 'password123',
          firstName: 'Test',
          lastName: 'User'
        });
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        expect(error.response.status).toBe(400);
        expect(error.response.data).toHaveProperty('error');
      }
    });

    it('should reject registration with weak password', async () => {
      try {
        await apiClient.post('/api/auth/register', {
          username: 'testuser',
          email: 'test@example.com',
          password: '123', // Too short
          firstName: 'Test',
          lastName: 'User'
        });
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        expect(error.response.status).toBe(400);
        expect(error.response.data).toHaveProperty('error');
      }
    });

    it('should reject duplicate email registration', async () => {
      // First registration
      await apiClient.post('/api/auth/register', testUser);
      
      // Second registration with same email should fail
      try {
        await apiClient.post('/api/auth/register', {
          ...testUser,
          username: 'different_username'
        });
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        expect(error.response.status).toBe(409); // Conflict
        expect(error.response.data).toHaveProperty('error');
      }
    });
  });

  describe('User Login', () => {
    beforeEach(async () => {
      // Register a user for login tests
      const response = await apiClient.post('/api/auth/register', testUser);
      registeredUserToken = response.data.token;
    });

    it('should login with valid credentials', async () => {
      const response = await apiClient.post('/api/auth/login', {
        email: testUser.email,
        password: testUser.password
      });

      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('token');
      expect(response.data.user).toHaveProperty('id');
      expect(response.data.user.email).toBe(testUser.email);
    });

    it('should reject login with invalid password', async () => {
      try {
        await apiClient.post('/api/auth/login', {
          email: testUser.email,
          password: 'wrongpassword'
        });
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        expect(error.response.status).toBe(401);
        expect(error.response.data).toHaveProperty('error');
      }
    });

    it('should reject login with non-existent email', async () => {
      try {
        await apiClient.post('/api/auth/login', {
          email: 'nonexistent@example.com',
          password: 'password123'
        });
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        expect(error.response.status).toBe(401);
        expect(error.response.data).toHaveProperty('error');
      }
    });

    it('should reject login with missing credentials', async () => {
      try {
        await apiClient.post('/api/auth/login', {
          email: testUser.email
          // Missing password
        });
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        expect(error.response.status).toBe(400);
        expect(error.response.data).toHaveProperty('error');
      }
    });
  });

  describe('Protected Routes', () => {
    let authToken;

    beforeEach(async () => {
      // Register and login to get auth token
      const registerResponse = await apiClient.post('/api/auth/register', testUser);
      registeredUserToken = registerResponse.data.token;
      
      const loginResponse = await apiClient.post('/api/auth/login', {
        email: testUser.email,
        password: testUser.password
      });
      authToken = loginResponse.data.token;
    });

    it('should access protected profile endpoint with valid token', async () => {
      const response = await apiClient.get('/api/users/profile', {
        headers: { Authorization: `Bearer ${authToken}` }
      });

      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('user');
      expect(response.data.user.email).toBe(testUser.email);
    });

    it('should reject protected endpoint without token', async () => {
      try {
        await apiClient.get('/api/users/profile');
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        expect(error.response.status).toBe(401);
        expect(error.response.data).toHaveProperty('error');
      }
    });

    it('should reject protected endpoint with invalid token', async () => {
      try {
        await apiClient.get('/api/users/profile', {
          headers: { Authorization: 'Bearer invalid-token' }
        });
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        expect(error.response.status).toBe(401);
        expect(error.response.data).toHaveProperty('error');
      }
    });

    it('should reject protected endpoint with malformed token', async () => {
      try {
        await apiClient.get('/api/users/profile', {
          headers: { Authorization: 'InvalidFormat' }
        });
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        expect(error.response.status).toBe(401);
        expect(error.response.data).toHaveProperty('error');
      }
    });
  });

  describe('Token Refresh', () => {
    let refreshToken;

    beforeEach(async () => {
      // Register user and get refresh token if available
      const response = await apiClient.post('/api/auth/register', testUser);
      registeredUserToken = response.data.token;
      // Note: This assumes the API returns a refresh token
      refreshToken = response.data.refreshToken || response.data.token;
    });

    it.skip('should refresh expired token', async () => {
      // This test is skipped as it requires token expiration logic
      // Implementation would depend on how refresh tokens are handled
      expect(true).toBe(true);
    });
  });
});