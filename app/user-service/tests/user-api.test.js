const request = require('supertest');
const mongoose = require('mongoose');
const { hashPassword, comparePasswords, generateTokens, verifyToken, validateEmail, validatePassword } = require('../utils');
const app = require('../server');

describe('User Service API', () => {
  let server;
  let testUser;
  let authToken;

  beforeAll(async () => {
    // Connect to test database
    await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/chatapp-test');
    server = app.listen(0); // Use random port for testing
  });

  afterAll(async () => {
    // Clean up test data
    await mongoose.connection.db.dropDatabase();
    await mongoose.connection.close();
    server.close();
  });

  beforeEach(async () => {
    // Clear collections before each test
    await mongoose.connection.db.dropDatabase();
  });

  describe('GET /', () => {
    it('should return service health status', async () => {
      const response = await request(app)
        .get('/')
        .expect(200);

      expect(response.body).toHaveProperty('message');
      expect(response.body.message).toBe('User Service is running');
    });
  });

  describe('POST /register', () => {
    const validUserData = {
      username: 'testuser',
      email: 'test@example.com',
      password: 'password123',
      firstName: 'Test',
      lastName: 'User'
    };

    it('should register a new user successfully', async () => {
      const response = await request(app)
        .post('/register')
        .send(validUserData)
        .expect(201);

      expect(response.body).toHaveProperty('user');
      expect(response.body).toHaveProperty('tokens');
      expect(response.body.user.username).toBe(validUserData.username);
      expect(response.body.user.email).toBe(validUserData.email);
    });

    it('should reject registration with missing required fields', async () => {
      const incompleteData = {
        username: 'testuser',
        email: 'test@example.com'
        // missing password
      };

      const response = await request(app)
        .post('/register')
        .send(incompleteData)
        .expect(400);

      expect(response.body).toHaveProperty('error');
    });

    it('should reject registration with weak password', async () => {
      const weakPasswordData = {
        ...validUserData,
        password: '123' // too short
      };

      const response = await request(app)
        .post('/register')
        .send(weakPasswordData)
        .expect(400);

      expect(response.body).toHaveProperty('error');
    });

    it('should reject duplicate email registration', async () => {
      // First registration
      await request(app)
        .post('/register')
        .send(validUserData);

      // Second registration with same email
      const response = await request(app)
        .post('/register')
        .send(validUserData)
        .expect(409);

      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toContain('already exists');
    });
  });

  describe('POST /login', () => {
    const loginCredentials = {
      email: 'test@example.com',
      password: 'password123'
    };

    beforeEach(async () => {
      // Create a test user
      await request(app)
        .post('/register')
        .send({
          username: 'testuser',
          email: 'test@example.com',
          password: 'password123',
          firstName: 'Test',
          lastName: 'User'
        });
    });

    it('should login user with valid credentials', async () => {
      const response = await request(app)
        .post('/login')
        .send(loginCredentials)
        .expect(200);

      expect(response.body).toHaveProperty('user');
      expect(response.body).toHaveProperty('tokens');
      expect(response.body.tokens).toHaveProperty('accessToken');
      expect(response.body.tokens).toHaveProperty('refreshToken');
      
      authToken = response.body.tokens.accessToken;
    });

    it('should reject login with invalid password', async () => {
      const response = await request(app)
        .post('/login')
        .send({
          ...loginCredentials,
          password: 'wrongpassword'
        })
        .expect(401);

      expect(response.body).toHaveProperty('error');
    });

    it('should reject login with non-existent email', async () => {
      const response = await request(app)
        .post('/login')
        .send({
          email: 'nonexistent@example.com',
          password: 'password123'
        })
        .expect(401);

      expect(response.body).toHaveProperty('error');
    });
  });

  describe('Authentication Required Routes', () => {
    let authToken;

    beforeEach(async () => {
      // Create and login user to get auth token
      const registerResponse = await request(app)
        .post('/register')
        .send({
          username: 'testuser',
          email: 'test@example.com',
          password: 'password123',
          firstName: 'Test',
          lastName: 'User'
        });

      authToken = registerResponse.body.tokens.accessToken;
    });

    describe('GET /profile', () => {
      it('should return user profile with valid token', async () => {
        const response = await request(app)
          .get('/profile')
          .set('Authorization', `Bearer ${authToken}`)
          .expect(200);

        expect(response.body).toHaveProperty('user');
        expect(response.body.user.email).toBe('test@example.com');
      });

      it('should reject request without token', async () => {
        await request(app)
          .get('/profile')
          .expect(401);
      });

      it('should reject request with invalid token', async () => {
        await request(app)
          .get('/profile')
          .set('Authorization', 'Bearer invalid-token')
          .expect(401);
      });
    });

    describe('PUT /profile', () => {
      it('should update user profile with valid data', async () => {
        const updateData = {
          firstName: 'Updated',
          lastName: 'Name',
          bio: 'Updated bio'
        };

        const response = await request(app)
          .put('/profile')
          .set('Authorization', `Bearer ${authToken}`)
          .send(updateData)
          .expect(200);

        expect(response.body.user.firstName).toBe('Updated');
        expect(response.body.user.lastName).toBe('Name');
        expect(response.body.user.bio).toBe('Updated bio');
      });

      it('should reject update with invalid data', async () => {
        const invalidData = {
          email: 'invalid-email' // Invalid email format
        };

        await request(app)
          .put('/profile')
          .set('Authorization', `Bearer ${authToken}`)
          .send(invalidData)
          .expect(400);
      });
    });

    describe('POST /logout', () => {
      it('should logout user successfully', async () => {
        await request(app)
          .post('/logout')
          .set('Authorization', `Bearer ${authToken}`)
          .expect(200);
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle database connection errors gracefully', async () => {
      // Temporarily close database connection
      await mongoose.connection.close();
      
      const response = await request(app)
        .get('/profile')
        .set('Authorization', 'Bearer fake-token')
        .expect(500);

      expect(response.body).toHaveProperty('error');
      
      // Reconnect for other tests
      await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/chatapp-test');
    });
  });
});