const request = require('supertest');
const app = require('../server');
const mongoose = require('mongoose');

describe('Profile Management Tests', () => {
    let server;
    let authToken;
    let testUser;

    beforeAll(async () => {
        const PORT = process.env.TEST_PORT || 3003;
        server = app.listen(PORT);
        
        testUser = {
            username: 'profileuser',
            email: 'profile@example.com',
            password: 'password123',
            firstName: 'Profile',
            lastName: 'User'
        };

        // Register and login to get auth token
        const registerResponse = await request(app)
            .post('/register')
            .send(testUser);
        
        authToken = registerResponse.body.tokens.accessToken;
    });

    afterAll(async () => {
        await mongoose.connection.db.dropDatabase();
        await mongoose.connection.close();
        server.close();
    });

    describe('GET /profile', () => {
        it('should return user profile with valid token', async () => {
            const response = await request(app)
                .get('/profile')
                .set('Authorization', `Bearer ${authToken}`)
                .expect(200);

            expect(response.body.user).toHaveProperty('id');
            expect(response.body.user.email).toBe(testUser.email);
            expect(response.body.user.username).toBe(testUser.username);
            expect(response.body.user.firstName).toBe(testUser.firstName);
            expect(response.body.user.lastName).toBe(testUser.lastName);
            expect(response.body.user).toHaveProperty('createdAt');
            expect(response.body.user).toHaveProperty('updatedAt');
        });

        it('should exclude sensitive information from profile', async () => {
            const response = await request(app)
                .get('/profile')
                .set('Authorization', `Bearer ${authToken}`)
                .expect(200);

            expect(response.body.user).not.toHaveProperty('password');
            expect(response.body.user).not.toHaveProperty('passwordHash');
        });
    });

    describe('PUT /profile', () => {
        it('should update user profile successfully', async () => {
            const updateData = {
                firstName: 'UpdatedFirstName',
                lastName: 'UpdatedLastName',
                bio: 'This is my updated bio'
            };

            const response = await request(app)
                .put('/profile')
                .set('Authorization', `Bearer ${authToken}`)
                .send(updateData)
                .expect(200);

            expect(response.body.user.firstName).toBe(updateData.firstName);
            expect(response.body.user.lastName).toBe(updateData.lastName);
            expect(response.body.user.bio).toBe(updateData.bio);
            expect(response.body.message).toBe('Profile updated successfully');
        });

        it('should update partial profile information', async () => {
            const updateData = {
                firstName: 'PartialUpdate'
            };

            const response = await request(app)
                .put('/profile')
                .set('Authorization', `Bearer ${authToken}`)
                .send(updateData)
                .expect(200);

            expect(response.body.user.firstName).toBe(updateData.firstName);
            // Other fields should remain unchanged
            expect(response.body.user.lastName).toBe('UpdatedLastName');
        });

        it('should reject profile update with invalid data', async () => {
            const invalidData = {
                firstName: '' // Empty string
            };

            const response = await request(app)
                .put('/profile')
                .set('Authorization', `Bearer ${authToken}`)
                .send(invalidData)
                .expect(400);

            expect(response.body.error).toContain('Invalid first name');
        });

        it('should reject profile update exceeding field limits', async () => {
            const longData = {
                firstName: 'A'.repeat(101), // Exceeds typical 100 char limit
                bio: 'B'.repeat(501) // Exceeds typical 500 char limit
            };

            const response = await request(app)
                .put('/profile')
                .set('Authorization', `Bearer ${authToken}`)
                .send(longData)
                .expect(400);

            expect(response.body.error).toContain('Field too long');
        });
    });

    describe('Password Management', () => {
        it('should change password successfully', async () => {
            const passwordData = {
                currentPassword: testUser.password,
                newPassword: 'newpassword123'
            };

            const response = await request(app)
                .put('/change-password')
                .set('Authorization', `Bearer ${authToken}`)
                .send(passwordData)
                .expect(200);

            expect(response.body.message).toBe('Password changed successfully');
        });

        it('should reject password change with wrong current password', async () => {
            const passwordData = {
                currentPassword: 'wrongpassword',
                newPassword: 'anotherpassword123'
            };

            const response = await request(app)
                .put('/change-password')
                .set('Authorization', `Bearer ${authToken}`)
                .send(passwordData)
                .expect(400);

            expect(response.body.error).toBe('Current password is incorrect');
        });

        it('should reject password change with weak new password', async () => {
            const passwordData = {
                currentPassword: 'newpassword123',
                newPassword: '123'
            };

            const response = await request(app)
                .put('/change-password')
                .set('Authorization', `Bearer ${authToken}`)
                .send(passwordData)
                .expect(400);

            expect(response.body.error).toContain('New password too weak');
        });

        it('should reject password change with missing fields', async () => {
            const incompleteData = {
                currentPassword: 'somepassword'
                // Missing newPassword
            };

            const response = await request(app)
                .put('/change-password')
                .set('Authorization', `Bearer ${authToken}`)
                .send(incompleteData)
                .expect(400);

            expect(response.body.error).toContain('Both current and new passwords required');
        });
    });
});