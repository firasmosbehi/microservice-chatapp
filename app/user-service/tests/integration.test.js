const axios = require('axios');

const BASE_URL = 'http://localhost:3001';
let authToken = '';
let refreshToken = '';

async function testUserService() {
    console.log('=== User Service Functional Test ===\n');

    try {
        // Test 1: Health Check
        console.log('1. Testing service health...');
        const healthResponse = await axios.get(`${BASE_URL}/`);
        console.log(`   ✓ Service is running: ${healthResponse.data.message}\n`);

        // Test 2: User Registration
        console.log('2. Registering new user...');
        const userData = {
            username: 'testuser123',
            email: 'test@example.com',
            password: 'password123',
            firstName: 'Test',
            lastName: 'User'
        };

        try {
            const registerResponse = await axios.post(`${BASE_URL}/register`, userData);
            console.log(`   ✓ User registered successfully`);
            console.log(`   User ID: ${registerResponse.data.user.id}`);
            console.log(`   Username: ${registerResponse.data.user.username}`);
            
            // Store tokens for later use
            authToken = registerResponse.data.tokens.accessToken;
            refreshToken = registerResponse.data.tokens.refreshToken;
            console.log(`   ✓ Tokens received\n`);
        } catch (error) {
            if (error.response?.status === 409) {
                console.log(`   ℹ User already exists, proceeding with login...\n`);
                
                // Test 3: User Login
                console.log('3. Logging in existing user...');
                const loginData = {
                    email: 'test@example.com',
                    password: 'password123'
                };

                const loginResponse = await axios.post(`${BASE_URL}/login`, loginData);
                console.log(`   ✓ Login successful`);
                console.log(`   Welcome back: ${loginResponse.data.user.firstName} ${loginResponse.data.user.lastName}`);
                
                authToken = loginResponse.data.tokens.accessToken;
                refreshToken = loginResponse.data.tokens.refreshToken;
                console.log(`   ✓ Tokens received\n`);
            } else {
                throw error;
            }
        }

        // Test 4: Get User Profile
        console.log('4. Getting user profile...');
        const profileResponse = await axios.get(`${BASE_URL}/profile`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        console.log(`   ✓ Profile retrieved`);
        console.log(`   Name: ${profileResponse.data.user.firstName} ${profileResponse.data.user.lastName}`);
        console.log(`   Email verified: ${profileResponse.data.user.emailVerified}\n`);

        // Test 5: Update Profile
        console.log('5. Updating user profile...');
        const updateData = {
            firstName: 'Updated Test',
            lastName: 'Updated User'
        };

        const updateResponse = await axios.put(`${BASE_URL}/profile`, updateData, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        console.log(`   ✓ Profile updated successfully`);
        console.log(`   New name: ${updateResponse.data.user.firstName} ${updateResponse.data.user.lastName}\n`);

        // Test 6: Change Password
        console.log('6. Changing password...');
        const passwordData = {
            currentPassword: 'password123',
            newPassword: 'newpassword123'
        };

        const passwordResponse = await axios.put(`${BASE_URL}/change-password`, passwordData, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        console.log(`   ✓ Password changed successfully\n`);

        // Test 7: Token Refresh
        console.log('7. Refreshing access token...');
        const refreshData = { refreshToken };

        const refreshResponse = await axios.post(`${BASE_URL}/refresh-token`, refreshData);
        console.log(`   ✓ Token refreshed successfully`);
        console.log(`   New access token length: ${refreshResponse.data.tokens.accessToken.length}\n`);

        // Test 8: Get All Users (Admin)
        console.log('8. Getting all users...');
        const usersResponse = await axios.get(`${BASE_URL}/users`);
        console.log(`   ✓ Retrieved ${usersResponse.data.users.length} users\n`);

        // Test 9: Logout
        console.log('9. Logging out...');
        const logoutResponse = await axios.post(`${BASE_URL}/logout`, {}, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        console.log(`   ✓ Logged out successfully\n`);

        console.log('=== All tests completed successfully! ===');

    } catch (error) {
        console.error('\n❌ Test failed:');
        if (error.response) {
            console.error(`   Status: ${error.response.status}`);
            console.error(`   Error: ${JSON.stringify(error.response.data)}`);
        } else {
            console.error(`   Error: ${error.message}`);
        }
    }
}

// Run the tests
testUserService();