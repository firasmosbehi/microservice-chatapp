module.exports = {
  testEnvironment: 'node',
  setupFilesAfterEnv: [],
  testMatch: [
    '<rootDir>/__integration-tests__/**/*.test.js'
  ],
  collectCoverageFrom: [
    'server.js',
    '!<rootDir>/node_modules/',
    '!<rootDir>/__tests__/',
    '!<rootDir>/tests/',
    '!<rootDir>/unit_tests/'
  ],
  testTimeout: 30000,
  verbose: true,
  // Mock external dependencies
  moduleNameMapper: {
    '^mongoose$': '<rootDir>/__mocks__/mongoose.js'
  }
};
