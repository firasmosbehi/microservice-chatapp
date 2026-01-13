const request = require('supertest');
const app = require('../server'); // Adjust path as needed
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

describe('Authentication Tests', () => {
    let server;
    let testUser;

    beforeAll(async () => {
        // Start server on test port
        const PORT = process.env.TEST_PORT || 3002;
        server = app.listen(PORT);
        
        // Create test user data
        testUser = {
            username: 'testuser',
            email: 'test@example.com',
            password: 'password123',
            firstName: 'Test',
            lastName: 'User'
        };
    });

    afterAll(async () => {
        // Clean up test data
        await mongoose.connection.db.dropDatabase();
        await mongoose.connection.close();
        server.close();
    });

    describe('POST /register', () => {
        it('should register a new user successfully', async () => {
            const response = await request(app)
                .post('/register')
                .send(testUser)
                .expect(201);

            expect(response.body).toHaveProperty('user');
            expect(response.body).toHaveProperty('tokens');
            expect(response.body.user.email).toBe(testUser.email);
            expect(response.body.user.username).toBe(testUser.username);
            expect(response.body.tokens).toHaveProperty('accessToken');
            expect(response.body.tokens).toHaveProperty('refreshToken');
        });

        it('should reject registration with duplicate email', async () => {
            // First registration
            await request(app)
                .post('/register')
                .send(testUser);

            // Second registration with same email
            const response = await request(app)
                .post('/register')
                .send(testUser)
                .expect(409);

            expect(response.body.error).toBe('User already exists');
        });

        it('should reject registration with invalid email', async () => {
            const invalidUser = { ...testUser, email: 'invalid-email' };
            
            const response = await request(app)
                .post('/register')
                .send(invalidUser)
                .expect(400);

            expect(response.body.error).toContain('Invalid email');
        });

        it('should reject registration with weak password', async () => {
            const weakUser = { ...testUser, password: '123' };
            
            const response = await request(app)
                .post('/register')
                .send(weakUser)
                .expect(400);

            expect(response.body.error).toContain('Password too weak');
        });

        it('should reject registration with missing required fields', async () => {
            const incompleteUser = { email: 'test@example.com' };
            
            const response = await request(app)
                .post('/register')
                .send(incompleteUser)
                .expect(400);

            expect(response.body.error).toContain('Missing required fields');
        });
    });

    describe('POST /login', () => {
        beforeEach(async () => {
            // Register user before each login test
            await request(app)
                .post('/register')
                .send(testUser);
        });

        it('should login user with correct credentials', async () => {
            const response = await request(app)
                .post('/login')
                .send({
                    email: testUser.email,
                    password: testUser.password
                })
                .expect(200);

            expect(response.body).toHaveProperty('user');
            expect(response.body).toHaveProperty('tokens');
            expect(response.body.user.email).toBe(testUser.email);
            expect(response.body.tokens).toHaveProperty('accessToken');
        });

        it('should reject login with incorrect password', async () => {
            const response = await request(app)
                .post('/login')
                .send({
                    email: testUser.email,
                    password: 'wrongpassword'
                })
                .expect(401);

            expect(response.body.error).toBe('Invalid credentials');
        });

        it('should reject login with non-existent email', async () => {
            const response = await request(app)
                .post('/login')
                .send({
                    email: 'nonexistent@example.com',
                    password: testUser.password
                })
                .expect(401);

            expect(response.body.error).toBe('Invalid credentials');
        });

        it('should reject login with missing credentials', async () => {
            const response = await request(app)
                .post('/login')
                .send({ email: testUser.email })
                .expect(400);

            expect(response.body.error).toContain('Email and password required');
        });
    });

    describe('Authentication Middleware', () => {
        let authToken;

        beforeEach(async () => {
            // Register and login to get auth token
            const registerResponse = await request(app)
                .post('/register')
                .send(testUser);
            
            authToken = registerResponse.body.tokens.accessToken;
        });

        it('should allow access with valid token', async () => {
            const response = await request(app)
                .get('/profile')
                .set('Authorization', `Bearer ${authToken}`)
                .expect(200);

            expect(response.body.user.email).toBe(testUser.email);
        });

        it('should reject access without token', async () => {
            const response = await request(app)
                .get('/profile')
                .expect(401);

            expect(response.body.error).toBe('Authentication required');
        });

        it('should reject access with invalid token', async () => {
            const response = await request(app)
                .get('/profile')
                .set('Authorization', 'Bearer invalid-token')
                .expect(401);

            expect(response.body.error).toBe('Invalid token');
        });

        it('should reject access with expired token', async () => {
            // Create expired token
            const expiredToken = jwt.sign(
                { userId: '123', email: 'test@example.com' },
                process.env.JWT_SECRET || 'secret',
                { expiresIn: '-1h' }
            );

            const response = await request(app)
                .get('/profile')
                .set('Authorization', `Bearer ${expiredToken}`)
                .expect(401);

            expect(response.body.error).toBe('Token expired');
        });
    });
});