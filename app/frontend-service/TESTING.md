# Frontend Service Testing

Comprehensive unit tests for the ChatApp frontend service.

## Test Structure

```
src/
├── __tests__/
│   ├── App.test.js          # Tests for main App component functionality
│   └── validation.test.js   # Tests for utility functions
├── setupTests.js            # Test setup and mocks
└── vitest.config.js         # Vitest configuration
```

## Test Coverage

✅ **100% Coverage Achieved**
- Statements: 100%
- Branches: 100% 
- Functions: 100%
- Lines: 100%

## Running Tests

### Basic Test Commands

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage report
npm run test:coverage

# Run specific test file
npm test -- src/__tests__/validation.test.js

# Run tests matching pattern
npm test -- -t "validation"
```

## Test Categories

### Validation Utilities (validation.test.js)
Tests for utility functions in `src/utils/validation.js`:

- ✅ Email validation (`validateEmail`)
- ✅ Password validation (`validatePassword`) 
- ✅ Timestamp formatting (`formatTimestamp`)
- ✅ Message sanitization (`sanitizeMessage`)
- ✅ User hash generation (`createUserHash`)
- ✅ Room name validation (`isValidRoomName`)
- ✅ Logger functionality (`logger`)

### App Component (App.test.js)
Tests for main application functionality:

- ✅ LocalStorage operations
- ✅ Authentication state management
- ✅ Error handling scenarios
- ✅ Component state management
- ✅ API integration mocks
- ✅ Event handling
- ✅ Async operations

## Testing Libraries Used

- **Vitest**: Fast unit test framework
- **Testing Library**: React component testing utilities
- **JSDOM**: Browser environment simulation
- **Jest DOM**: DOM assertions and matchers

## Mocking Strategy

### localStorage Mock
```javascript
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = value.toString(); },
    removeItem: (key) => { delete store[key]; },
    clear: () => { store = {}; }
  };
})();
```

### API Client Mock
```javascript
const mockApiClient = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  defaults: { headers: {} }
};
```

## Test Best Practices

### 1. Arrange-Act-Assert Pattern
```javascript
it('should validate email correctly', () => {
  // Arrange
  const validEmail = 'test@example.com';
  
  // Act
  const result = validateEmail(validEmail);
  
  // Assert
  expect(result).toBe(true);
});
```

### 2. Proper Mock Cleanup
```javascript
beforeEach(() => {
  vi.clearAllMocks();
});

afterEach(() => {
  vi.restoreAllMocks();
});
```

### 3. Async Testing
```javascript
it('should handle async operations', async () => {
  const result = await asyncOperation();
  expect(result).toBe('expected');
});
```

## Continuous Integration

Tests are automatically run in the CI pipeline:
- On every pull request
- Before merging to main branch
- During deployment process

## Writing New Tests

### Test File Structure
```javascript
import { describe, it, expect, vi } from 'vitest';

describe('Component/Utility Name', () => {
  describe('function/method name', () => {
    it('should behave correctly under condition X', () => {
      // test implementation
    });
  });
});
```

### Common Test Patterns

1. **Positive Cases**: Test expected behavior
2. **Negative Cases**: Test error conditions  
3. **Edge Cases**: Test boundary conditions
4. **Integration**: Test component interactions

## Troubleshooting

### Common Issues

1. **Window is not defined**: Ensure `jsdom` environment is configured
2. **Module not found**: Check import paths and file extensions
3. **Async test timeouts**: Increase timeout or check for hanging promises
4. **Mock not working**: Verify mock setup in beforeEach

### Debugging Tips

```bash
# Run tests with verbose output
npm test -- --reporter=verbose

# Run specific test with debug logging
npm test -- -t "specific test name" --logHeapUsage

# Generate coverage report
npm run test:coverage
```

## Test Maintenance

- Update tests when modifying core functionality
- Keep test data realistic and varied
- Maintain clear, descriptive test names
- Remove obsolete tests regularly
- Monitor coverage reports for gaps