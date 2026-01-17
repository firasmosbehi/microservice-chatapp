// Integration test setup file
import { afterEach } from 'vitest';

// Global test configuration
global.TEST_CONFIG = {
  apiBaseUrl: process.env.TEST_API_BASE_URL || 'http://localhost:8000',
  timeout: parseInt(process.env.TEST_TIMEOUT) || 15000,
  cleanup: process.env.TEST_CLEANUP !== 'false'
};

// Global cleanup after each test
afterEach(async () => {
  // Add any global cleanup logic here if needed
  // This runs after each test file
});

// Mock console methods to reduce test noise
console.debug = () => {};
console.info = () => {};
console.warn = () => {};
console.error = () => {};

export {};