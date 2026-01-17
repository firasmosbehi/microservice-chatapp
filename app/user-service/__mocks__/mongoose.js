// Mock mongoose module for integration tests
const mongoose = {
  connect: jest.fn().mockResolvedValue(),
  connection: {
    on: jest.fn(),
    once: jest.fn((event, callback) => {
      if (event === 'open') {
        setTimeout(callback, 100); // Simulate async connection
      }
    }),
    close: jest.fn().mockResolvedValue()
  }
};

module.exports = mongoose;
