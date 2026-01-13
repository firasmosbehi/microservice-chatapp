#!/usr/bin/env node

/**
 * User Service Test Runner
 * Runs all unit tests with proper setup and teardown
 */

const { spawn } = require('child_process');
const path = require('path');

// Colors for output
const colors = {
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  reset: '\x1b[0m'
};

function log(color, message) {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function runTests() {
  log('blue', '🚀 Starting User Service Unit Tests...');
  log('blue', '=====================================');
  
  // Set environment variables for testing
  const env = {
    ...process.env,
    NODE_ENV: 'test',
    MONGODB_URI: process.env.MONGODB_URI || 'mongodb://localhost:27017/chatapp-test',
    JWT_SECRET: 'test-secret-key-for-testing',
    PORT: '0' // Use random port
  };

  // Run Jest with coverage
  const jestProcess = spawn('npx', [
    'jest',
    '--testMatch=**/tests/core-functions.test.js,**/tests/user-utils-simple.test.js',
    '--coverage',
    '--verbose',
    '--detectOpenHandles',
    '--forceExit'
  ], {
    cwd: path.join(__dirname, '..'),
    env,
    stdio: 'inherit'
  });

  jestProcess.on('close', (code) => {
    if (code === 0) {
      log('green', '\n✅ All User Service tests passed!');
      log('cyan', '📊 Test coverage report generated in coverage/ directory');
    } else {
      log('red', `\n❌ User Service tests failed with exit code ${code}`);
      process.exit(code);
    }
  });

  jestProcess.on('error', (error) => {
    log('red', `Failed to start test process: ${error.message}`);
    process.exit(1);
  });
}

// Check if required dependencies are installed
function checkDependencies() {
  try {
    require('jest');
    require('supertest');
    log('green', '✅ All test dependencies are available');
    return true;
  } catch (error) {
    log('yellow', '⚠️  Installing test dependencies...');
    const installProcess = spawn('npm', ['install', 'jest', 'supertest', '@types/jest', 'jest-environment-node'], {
      cwd: path.join(__dirname, '..'),
      stdio: 'inherit'
    });

    installProcess.on('close', (code) => {
      if (code === 0) {
        log('green', '✅ Dependencies installed successfully');
        runTests();
      } else {
        log('red', '❌ Failed to install dependencies');
        process.exit(1);
      }
    });
    return false;
  }
}

// Create jest config if it doesn't exist
function createJestConfig() {
  const fs = require('fs');
  const configPath = path.join(__dirname, '../jest.config.js');
  
  if (!fs.existsSync(configPath)) {
    const config = `
module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.js'],
  collectCoverageFrom: [
    '**/*.js',
    '!**/node_modules/**',
    '!**/tests/**',
    '!jest.config.js',
    '!run_tests.js'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  testTimeout: 10000
};`;
    
    fs.writeFileSync(configPath, config.trim());
    log('green', '✅ Created Jest configuration file');
  }
}

// Create test setup file
function createTestSetup() {
  const fs = require('fs');
  const setupPath = path.join(__dirname, '../tests/setup.js');
  
  if (!fs.existsSync(setupPath)) {
    const setup = `
// Test setup file
process.env.NODE_ENV = 'test';
process.env.JWT_SECRET = 'test-secret-key';

// Extend Jest expectations
expect.extend({
  toBeType(received, expected) {
    const type = typeof received;
    if (type === expected) {
      return {
        message: () => \`expected \${received} not to be type \${expected}\`,
        pass: true
      };
    } else {
      return {
        message: () => \`expected \${received} to be type \${expected} but was \${type}\`,
        pass: false
      };
    }
  }
});`;
    
    fs.writeFileSync(setupPath, setup.trim());
    log('green', '✅ Created test setup file');
  }
}

// Main execution
if (require.main === module) {
  createJestConfig();
  createTestSetup();
  
  if (checkDependencies()) {
    runTests();
  }
}

module.exports = { runTests };