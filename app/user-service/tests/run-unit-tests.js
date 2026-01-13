#!/usr/bin/env node

/**
 * User Service Unit Test Runner
 * Runs all unit tests with proper setup and teardown
 */

const { spawn } = require('child_process');
const path = require('path');

async function runTests() {
    console.log('🚀 Starting User Service Unit Tests...\n');
    
    // Test files in order of dependency
    const testFiles = [
        'unit_tests/auth.test.js',
        'unit_tests/profile.test.js', 
        'unit_tests/token.test.js',
        'unit_tests/userManagement.test.js'
    ];
    
    let passedTests = 0;
    let failedTests = 0;
    
    for (const testFile of testFiles) {
        console.log(`🧪 Running ${testFile}...`);
        
        try {
            const result = await runSingleTest(testFile);
            if (result.success) {
                passedTests++;
                console.log(`✅ ${testFile} passed\n`);
            } else {
                failedTests++;
                console.log(`❌ ${testFile} failed\n`);
                console.log(result.output);
            }
        } catch (error) {
            failedTests++;
            console.log(`❌ ${testFile} crashed: ${error.message}\n`);
        }
    }
    
    console.log('📊 Test Results Summary:');
    console.log(`✅ Passed: ${passedTests}`);
    console.log(`❌ Failed: ${failedTests}`);
    console.log(`📋 Total: ${passedTests + failedTests}\n`);
    
    if (failedTests === 0) {
        console.log('🎉 All tests passed!');
        process.exit(0);
    } else {
        console.log('💥 Some tests failed!');
        process.exit(1);
    }
}

function runSingleTest(testFile) {
    return new Promise((resolve) => {
        const jestProcess = spawn('npx', ['jest', testFile, '--verbose'], {
            cwd: process.cwd(),
            env: {
                ...process.env,
                NODE_ENV: 'test',
                TEST_PORT: (3000 + Math.floor(Math.random() * 1000)).toString()
            }
        });
        
        let output = '';
        
        jestProcess.stdout.on('data', (data) => {
            output += data.toString();
        });
        
        jestProcess.stderr.on('data', (data) => {
            output += data.toString();
        });
        
        jestProcess.on('close', (code) => {
            resolve({
                success: code === 0,
                output: output
            });
        });
        
        // Timeout after 30 seconds
        setTimeout(() => {
            jestProcess.kill();
            resolve({
                success: false,
                output: 'Test timed out after 30 seconds'
            });
        }, 30000);
    });
}

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Test run interrupted');
    process.exit(1);
});

// Run the tests
runTests().catch(error => {
    console.error('💥 Test runner failed:', error);
    process.exit(1);
});