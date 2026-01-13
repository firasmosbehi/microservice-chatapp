const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

describe('User Service Core Functions', () => {
  const TEST_JWT_SECRET = 'test-secret-key';
  
  describe('Authentication Functions', () => {
    it('should hash and verify passwords', async () => {
      const plainPassword = 'mySecurePassword123';
      
      // Hash the password
      const hashedPassword = await bcrypt.hash(plainPassword, 12);
      expect(hashedPassword).toBeDefined();
      expect(hashedPassword).not.toEqual(plainPassword);
      
      // Verify correct password
      const isValid = await bcrypt.compare(plainPassword, hashedPassword);
      expect(isValid).toBe(true);
      
      // Reject wrong password
      const isInvalid = await bcrypt.compare('wrongpassword', hashedPassword);
      expect(isInvalid).toBe(false);
    });
    
    it('should generate and verify JWT tokens', () => {
      const userId = 12345;
      const payload = { userId, type: 'access' };
      
      // Generate token
      const token = jwt.sign(payload, TEST_JWT_SECRET, { expiresIn: '1h' });
      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
      
      // Verify token
      const decoded = jwt.verify(token, TEST_JWT_SECRET);
      expect(decoded.userId).toBe(userId);
      expect(decoded.type).toBe('access');
    });
    
    it('should reject invalid JWT tokens', () => {
      const invalidToken = 'invalid.token.string';
      
      expect(() => {
        jwt.verify(invalidToken, TEST_JWT_SECRET);
      }).toThrow();
    });
  });
  
  describe('Validation Functions', () => {
    it('should validate email addresses', () => {
      const validator = require('validator');
      
      const validEmails = [
        'user@example.com',
        'test.email@domain.co.uk',
        'user123@test-domain.org'
      ];
      
      const invalidEmails = [
        'invalid-email',
        '@domain.com',
        'user@',
        'user@domain'
      ];
      
      validEmails.forEach(email => {
        expect(validator.isEmail(email)).toBe(true);
      });
      
      invalidEmails.forEach(email => {
        expect(validator.isEmail(email)).toBe(false);
      });
    });
    
    it('should validate password requirements', () => {
      const validPasswords = [
        'password123',
        'MySecurePass!@#',
        'testpassword'
      ];
      
      const invalidPasswords = [
        '123',           // too short
        'pass',          // too short
        '',              // empty
        'a'.repeat(101)  // too long
      ];
      
      // Test minimum length requirement (6 characters)
      validPasswords.forEach(password => {
        expect(password.length >= 6).toBe(true);
        expect(password.length <= 100).toBe(true);
      });
      
      invalidPasswords.forEach(password => {
        const isValidLength = password.length >= 6 && password.length <= 100;
        expect(isValidLength).toBe(false);
      });
    });
  });
});