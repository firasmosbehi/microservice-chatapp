const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { 
  hashPassword, 
  comparePasswords, 
  generateTokens, 
  verifyToken,
  validateEmail,
  validatePassword 
} = require('../server');

describe('User Service Utilities', () => {
  describe('Password Hashing', () => {
    it('should hash password correctly', async () => {
      const password = 'testpassword123';
      const hashedPassword = await hashPassword(password);
      
      expect(hashedPassword).toBeDefined();
      expect(hashedPassword).not.toBe(password);
      expect(hashedPassword.length).toBeGreaterThan(password.length);
    });

    it('should verify correct password', async () => {
      const password = 'testpassword123';
      const hashedPassword = await hashPassword(password);
      const isValid = await comparePasswords(password, hashedPassword);
      
      expect(isValid).toBe(true);
    });

    it('should reject incorrect password', async () => {
      const password = 'testpassword123';
      const wrongPassword = 'wrongpassword';
      const hashedPassword = await hashPassword(password);
      const isValid = await comparePasswords(wrongPassword, hashedPassword);
      
      expect(isValid).toBe(false);
    });
  });

  describe('JWT Token Generation', () => {
    it('should generate valid access and refresh tokens', () => {
      const userId = 123;
      const tokens = generateTokens(userId);
      
      expect(tokens).toHaveProperty('accessToken');
      expect(tokens).toHaveProperty('refreshToken');
      expect(tokens.accessToken).toBeDefined();
      expect(tokens.refreshToken).toBeDefined();
    });

    it('should verify valid token', () => {
      const userId = 123;
      const tokens = generateTokens(userId);
      const decoded = verifyToken(tokens.accessToken);
      
      expect(decoded).toHaveProperty('userId');
      expect(decoded.userId).toBe(userId);
    });

    it('should reject invalid token', () => {
      const invalidToken = 'invalid.token.here';
      const decoded = verifyToken(invalidToken);
      
      expect(decoded).toBeNull();
    });

    it('should reject expired token', () => {
      // Create expired token
      const expiredToken = jwt.sign(
        { userId: 123 }, 
        process.env.JWT_SECRET || 'test-secret',
        { expiresIn: '0s' }
      );
      
      // Wait a bit for token to expire
      setTimeout(() => {
        const decoded = verifyToken(expiredToken);
        expect(decoded).toBeNull();
      }, 100);
    });
  });

  describe('Email Validation', () => {
    it('should accept valid email addresses', () => {
      const validEmails = [
        'test@example.com',
        'user.name@domain.co.uk',
        'test123@test-domain.org'
      ];

      validEmails.forEach(email => {
        expect(validateEmail(email)).toBe(true);
      });
    });

    it('should reject invalid email addresses', () => {
      const invalidEmails = [
        'invalid-email',
        '@domain.com',
        'user@',
        'user@domain',
        ''
      ];

      invalidEmails.forEach(email => {
        expect(validateEmail(email)).toBe(false);
      });
    });
  });

  describe('Password Validation', () => {
    it('should accept strong passwords', () => {
      const strongPasswords = [
        'password123',
        'StrongPass123!',
        'mypassword123'
      ];

      strongPasswords.forEach(password => {
        expect(validatePassword(password)).toBe(true);
      });
    });

    it('should reject weak passwords', () => {
      const weakPasswords = [
        '123',
        'pass',
        '',
        'a'.repeat(101) // too long
      ];

      weakPasswords.forEach(password => {
        expect(validatePassword(password)).toBe(false);
      });
    });

    it('should enforce minimum length', () => {
      const shortPassword = 'pass'; // less than 6 characters
      expect(validatePassword(shortPassword)).toBe(false);
    });

    it('should enforce maximum length', () => {
      const longPassword = 'a'.repeat(101); // more than 100 characters
      expect(validatePassword(longPassword)).toBe(false);
    });
  });

  describe('Integration Tests', () => {
    it('should handle complete authentication flow', async () => {
      const password = 'testpassword123';
      const userId = 456;

      // Hash password
      const hashedPassword = await hashPassword(password);
      
      // Verify password
      const isPasswordValid = await comparePasswords(password, hashedPassword);
      expect(isPasswordValid).toBe(true);

      // Generate tokens
      const tokens = generateTokens(userId);
      expect(tokens.accessToken).toBeDefined();
      expect(tokens.refreshToken).toBeDefined();

      // Verify token
      const decoded = verifyToken(tokens.accessToken);
      expect(decoded.userId).toBe(userId);
    });
  });
});