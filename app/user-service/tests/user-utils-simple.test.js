const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

describe('User Service Utilities', () => {
  describe('Password Hashing', () => {
    it('should hash password correctly', async () => {
      const password = 'testpassword123';
      const hashedPassword = await bcrypt.hash(password, 12);
      
      expect(hashedPassword).toBeDefined();
      expect(hashedPassword).not.toBe(password);
      expect(hashedPassword.length).toBeGreaterThan(password.length);
    });

    it('should verify correct password', async () => {
      const password = 'testpassword123';
      const hashedPassword = await bcrypt.hash(password, 12);
      const isValid = await bcrypt.compare(password, hashedPassword);
      
      expect(isValid).toBe(true);
    });

    it('should reject incorrect password', async () => {
      const password = 'testpassword123';
      const wrongPassword = 'wrongpassword';
      const hashedPassword = await bcrypt.hash(password, 12);
      const isValid = await bcrypt.compare(wrongPassword, hashedPassword);
      
      expect(isValid).toBe(false);
    });
  });

  describe('JWT Token Generation', () => {
    const JWT_SECRET = 'test-secret-key';
    
    it('should generate valid access and refresh tokens', () => {
      const userId = 123;
      
      const accessToken = jwt.sign(
        { userId, type: 'access' },
        JWT_SECRET,
        { expiresIn: '15m' }
      );
      
      const refreshToken = jwt.sign(
        { userId, type: 'refresh' },
        JWT_SECRET,
        { expiresIn: '7d' }
      );
      
      expect(accessToken).toBeDefined();
      expect(refreshToken).toBeDefined();
    });

    it('should verify valid token', () => {
      const userId = 123;
      const token = jwt.sign({ userId }, JWT_SECRET, { expiresIn: '1h' });
      const decoded = jwt.verify(token, JWT_SECRET);
      
      expect(decoded).toHaveProperty('userId');
      expect(decoded.userId).toBe(userId);
    });

    it('should reject invalid token', () => {
      const invalidToken = 'invalid.token.here';
      expect(() => {
        jwt.verify(invalidToken, JWT_SECRET);
      }).toThrow();
    });
  });

  describe('Validation', () => {
    it('should validate email format', () => {
      const validEmails = [
        'test@example.com',
        'user.name@domain.co.uk'
      ];
      
      const invalidEmails = [
        'invalid-email',
        '@domain.com',
        'user@'
      ];
      
      validEmails.forEach(email => {
        expect(require('validator').isEmail(email)).toBe(true);
      });
      
      invalidEmails.forEach(email => {
        expect(require('validator').isEmail(email)).toBe(false);
      });
    });

    it('should validate password strength', () => {
      const validPasswords = [
        'password123',
        'StrongPass123!'
      ];
      
      const invalidPasswords = [
        '123',
        'pass',
        'a'.repeat(101)
      ];
      
      validPasswords.forEach(password => {
        expect(password.length >= 6 && password.length <= 100).toBe(true);
      });
      
      invalidPasswords.forEach(password => {
        expect(password.length >= 6 && password.length <= 100).toBe(false);
      });
    });
  });
});