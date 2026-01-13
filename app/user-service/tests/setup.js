// Test setup file
process.env.NODE_ENV = 'test';
process.env.JWT_SECRET = 'test-secret-key';

// Extend Jest expectations
expect.extend({
  toBeType(received, expected) {
    const type = typeof received;
    if (type === expected) {
      return {
        message: () => `expected ${received} not to be type ${expected}`,
        pass: true
      };
    } else {
      return {
        message: () => `expected ${received} to be type ${expected} but was ${type}`,
        pass: false
      };
    }
  }
});