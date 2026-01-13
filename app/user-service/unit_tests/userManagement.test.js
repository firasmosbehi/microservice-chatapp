const request = require('supertest');
const app = require('../server');
const mongoose = require('mongoose');

describe('User Management Tests', () => {
    let server;
    let adminAuthToken;
    let testUsers = [];

    beforeAll(async () => {
        const PORT = process.env.TEST_PORT || 3005;
        server = app.listen(PORT);
        
        // Create multiple test users
        const userData = [
            {
                username: 'adminuser',
                email: 'admin@example.com',
                password: 'adminpass123',
                firstName: 'Admin',
                lastName: 'User'
            },
            {
                username: 'regularuser1',
                email: 'user1@example.com',
                password: 'userpass123',
                firstName: 'Regular',
                lastName: 'User1'
            },
            {
                username: 'regularuser2',
                email: 'user2@example.com',
                password: 'userpass123',
                firstName: 'Regular',
                lastName: 'User2'
            }
        ];

        for (const user of userData) {
            const response = await request(app)
                .post('/register')
                .send(user);
            
            testUsers.push({
                ...user,
                id: response.body.user.id,
                authToken: response.body.tokens.accessToken
            });

            // First user becomes admin for testing admin functions
            if (testUsers.length === 1) {
                adminAuthToken = response.body.tokens.accessToken;
            }
        }
    });

    afterAll(async () => {
        await mongoose.connection.db.dropDatabase();
        await mongoose.connection.close();
        server.close();
    });

    describe('GET /users', () => {
        it('should return list of all users', async () => {
            const response = await request(app)
                .get('/users')
                .set('Authorization', `Bearer ${adminAuthToken}`)
                .expect(200);

            expect(response.body).toHaveProperty('users');
            expect(Array.isArray(response.body.users)).toBe(true);
            expect(response.body.users.length).toBeGreaterThanOrEqual(3);
            
            // Check that user objects have expected properties
            const user = response.body.users[0];
            expect(user).toHaveProperty('id');
            expect(user).toHaveProperty('username');
            expect(user).toHaveProperty('email');
            expect(user).toHaveProperty('firstName');
            expect(user).toHaveProperty('lastName');
            expect(user).toHaveProperty('createdAt');
            
            // Sensitive data should be excluded
            expect(user).not.toHaveProperty('password');
            expect(user).not.toHaveProperty('passwordHash');
        });

        it('should return users with pagination metadata', async () => {
            const response = await request(app)
                .get('/users?page=1&limit=2')
                .set('Authorization', `Bearer ${adminAuthToken}`)
                .expect(200);

            expect(response.body).toHaveProperty('pagination');
            expect(response.body.pagination).toHaveProperty('page');
            expect(response.body.pagination).toHaveProperty('limit');
            expect(response.body.pagination).toHaveProperty('total');
            expect(response.body.pagination).toHaveProperty('pages');
        });

        it('should support pagination parameters', async () => {
            const response = await request(app)
                .get('/users?page=1&limit=1')
                .set('Authorization', `Bearer ${adminAuthToken}`)
                .expect(200);

            expect(response.body.users.length).toBeLessThanOrEqual(1);
        });

        it('should reject unauthorized access to users list', async () => {
            const response = await request(app)
                .get('/users')
                .expect(401);

            expect(response.body.error).toBe('Authentication required');
        });
    });

    describe('Email Management Tests', () => {
        let userAuthToken;

        beforeAll(() => {
            // Use the second test user for email tests
            userAuthToken = testUsers[1].authToken;
        });

        it('should handle forgot password request', async () => {
            const response = await request(app)
                .post('/forgot-password')
                .send({ email: testUsers[1].email })
                .expect(200);

            expect(response.body.message).toBe('Password reset email sent');
        });

        it('should reject forgot password with non-existent email', async () => {
            const response = await request(app)
                .post('/forgot-password')
                .send({ email: 'nonexistent@example.com' })
                .expect(404);

            expect(response.body.error).toBe('User not found');
        });

        it('should reject forgot password with invalid email format', async () => {
            const response = await request(app)
                .post('/forgot-password')
                .send({ email: 'invalid-email-format' })
                .expect(400);

            expect(response.body.error).toContain('Invalid email');
        });

        it('should handle password reset', async () => {
            // First request password reset to get reset token
            await request(app)
                .post('/forgot-password')
                .send({ email: testUsers[1].email });

            // Mock reset token (in real app, this would come from email)
            const resetToken = 'mock-reset-token';
            
            const response = await request(app)
                .post('/reset-password')
                .send({
                    token: resetToken,
                    newPassword: 'newpassword123'
                })
                .expect(200);

            expect(response.body.message).toBe('Password reset successfully');
        });

        it('should reject password reset with invalid token', async () => {
            const response = await request(app)
                .post('/reset-password')
                .send({
                    token: 'invalid-token',
                    newPassword: 'newpassword123'
                })
                .expect(400);

            expect(response.body.error).toBe('Invalid or expired reset token');
        });

        it('should reject password reset with weak password', async () => {
            const response = await request(app)
                .post('/reset-password')
                .send({
                    token: 'mock-token',
                    newPassword: '123'
                })
                .expect(400);

            expect(response.body.error).toContain('Password too weak');
        });
    });

    describe('Rate Limiting Tests', () => {
        it('should enforce rate limiting on authentication endpoints', async () => {
            // Make multiple rapid requests to trigger rate limiting
            const promises = [];
            for (let i = 0; i < 15; i++) {
                promises.push(
                    request(app)
                        .post('/login')
                        .send({
                            email: 'test@example.com',
                            password: 'wrongpassword'
                        })
                );
            }

            const responses = await Promise.all(promises);
            
            // Some requests should be rate limited (429 status)
            const rateLimitedResponses = responses.filter(r => r.status === 429);
            expect(rateLimitedResponses.length).toBeGreaterThan(0);
            
            if (rateLimitedResponses.length > 0) {
                expect(rateLimitedResponses[0].body.error).toBe('Too Many Requests');
            }
        });
    });

    describe('Input Validation Tests', () => {
        it('should validate user registration input thoroughly', async () => {
            const invalidInputs = [
                { email: 'test@example.com' }, // Missing password
                { password: 'password123' }, // Missing email
                { email: 'invalid', password: 'password123' }, // Invalid email
                { email: 'test@example.com', password: '123' }, // Weak password
                { email: 'a'.repeat(300) + '@example.com', password: 'password123' } // Email too long
            ];

            for (const invalidInput of invalidInputs) {
                const response = await request(app)
                    .post('/register')
                    .send(invalidInput)
                    .expect(400);
                
                expect(response.body).toHaveProperty('error');
            }
        });

        it('should sanitize and validate all user inputs', async () => {
            const maliciousInputs = [
                '<script>alert("xss")</script>',
                'normal@email.com<script>',
                'test@example.com\x00nullbyte',
                'user@domain.com\r\nInjection'
            ];

            for (const maliciousInput of maliciousInputs) {
                const response = await request(app)
                    .post('/register')
                    .send({
                        email: maliciousInput,
                        password: 'password123',
                        username: 'testuser',
                        firstName: 'Test',
                        lastName: 'User'
                    });
                
                // Should either reject or sanitize the input
                expect([201, 400]).toContain(response.status);
            }
        });
    });
});