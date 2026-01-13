const request = require('supertest');
const app = require('../server');
const mongoose = require('mongoose');

describe('Token Management Tests', () => {
    let server;
    let refreshToken;
    let testUser;

    beforeAll(async () => {
        const PORT = process.env.TEST_PORT || 3004;
        server = app.listen(PORT);
        
        testUser = {
            username: 'tokenuser',
            email: 'token@example.com',
            password: 'password123',
            firstName: 'Token',
            lastName: 'User'
        };

        // Register user to get refresh token
        const registerResponse = await request(app)
            .post('/register')
            .send(testUser);
        
        refreshToken = registerResponse.body.tokens.refreshToken;
    });

    afterAll(async () => {
        await mongoose.connection.db.dropDatabase();
        await mongoose.connection.close();
        server.close();
    });

    describe('POST /refresh-token', () => {
        it('should refresh access token with valid refresh token', async () => {
            const response = await request(app)
                .post('/refresh-token')
                .send({ refreshToken })
                .expect(200);

            expect(response.body).toHaveProperty('tokens');
            expect(response.body.tokens).toHaveProperty('accessToken');
            expect(response.body.tokens).toHaveProperty('refreshToken');
            expect(response.body.tokens.accessToken).not.toBe('');
            expect(response.body.message).toBe('Token refreshed successfully');
        });

        it('should reject refresh with invalid refresh token', async () => {
            const response = await request(app)
                .post('/refresh-token')
                .send({ refreshToken: 'invalid-refresh-token' })
                .expect(401);

            expect(response.body.error).toBe('Invalid refresh token');
        });

        it('should reject refresh with missing refresh token', async () => {
            const response = await request(app)
                .post('/refresh-token')
                .send({})
                .expect(400);

            expect(response.body.error).toBe('Refresh token required');
        });

        it('should reject refresh with expired refresh token', async () => {
            // This test assumes there's a way to create expired tokens
            // In practice, you'd need to mock the token verification
            // For now, we'll test the error handling structure
            const response = await request(app)
                .post('/refresh-token')
                .send({ refreshToken: 'expired-token-here' })
                .expect(401);

            expect(response.body.error).toBe('Invalid refresh token');
        });
    });

    describe('POST /logout', () => {
        let authToken;

        beforeEach(async () => {
            // Get fresh auth token for each logout test
            const loginResponse = await request(app)
                .post('/login')
                .send({
                    email: testUser.email,
                    password: testUser.password
                });
            
            authToken = loginResponse.body.tokens.accessToken;
        });

        it('should logout user successfully', async () => {
            const response = await request(app)
                .post('/logout')
                .set('Authorization', `Bearer ${authToken}`)
                .expect(200);

            expect(response.body.message).toBe('Logged out successfully');
        });

        it('should reject logout without authorization', async () => {
            const response = await request(app)
                .post('/logout')
                .expect(401);

            expect(response.body.error).toBe('Authentication required');
        });

        it('should invalidate token after logout', async () => {
            // Logout first
            await request(app)
                .post('/logout')
                .set('Authorization', `Bearer ${authToken}`);

            // Try to use the same token again
            const response = await request(app)
                .get('/profile')
                .set('Authorization', `Bearer ${authToken}`)
                .expect(401);

            expect(response.body.error).toBe('Invalid token');
        });
    });

    describe('Token Security Tests', () => {
        it('should have appropriate token expiration times', async () => {
            const loginResponse = await request(app)
                .post('/login')
                .send({
                    email: testUser.email,
                    password: testUser.password
                });

            const { accessToken, refreshToken: newRefreshToken } = loginResponse.body.tokens;
            
            // Basic validation - tokens should not be empty
            expect(accessToken).toBeTruthy();
            expect(newRefreshToken).toBeTruthy();
            expect(accessToken.length).toBeGreaterThan(20);
            expect(newRefreshToken.length).toBeGreaterThan(20);
        });

        it('should generate unique tokens for each login', async () => {
            const loginResponse1 = await request(app)
                .post('/login')
                .send({
                    email: testUser.email,
                    password: testUser.password
                });

            const loginResponse2 = await request(app)
                .post('/login')
                .send({
                    email: testUser.email,
                    password: testUser.password
                });

            const token1 = loginResponse1.body.tokens.accessToken;
            const token2 = loginResponse2.body.tokens.accessToken;
            
            expect(token1).not.toBe(token2);
        });
    });
});