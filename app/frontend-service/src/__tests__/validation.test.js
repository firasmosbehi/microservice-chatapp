import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { 
  validateEmail, 
  validatePassword, 
  formatTimestamp, 
  sanitizeMessage, 
  createUserHash, 
  isValidRoomName,
  logger
} from '../utils/validation';

describe('Validation Utilities', () => {
  describe('validateEmail', () => {
    it('should return true for valid emails', () => {
      expect(validateEmail('test@example.com')).toBe(true);
      expect(validateEmail('user.name@domain.co.uk')).toBe(true);
      expect(validateEmail('test+tag@example.org')).toBe(true);
    });

    it('should return false for invalid emails', () => {
      expect(validateEmail('invalid')).toBe(false);
      expect(validateEmail('test@')).toBe(false);
      expect(validateEmail('@example.com')).toBe(false);
      expect(validateEmail('test.example.com')).toBe(false);
      expect(validateEmail('')).toBe(false);
    });
  });

  describe('validatePassword', () => {
    it('should return true for passwords with 6 or more characters', () => {
      expect(validatePassword('123456')).toBe(true);
      expect(validatePassword('password')).toBe(true);
      expect(validatePassword('a'.repeat(20))).toBe(true);
    });

    it('should return false for passwords with less than 6 characters', () => {
      expect(validatePassword('')).toBe(false);
      expect(validatePassword('12345')).toBe(false);
      expect(validatePassword('a')).toBe(false);
    });
  });

  describe('formatTimestamp', () => {
    beforeEach(() => {
      // Mock console methods to avoid test noise
      vi.spyOn(console, 'info').mockImplementation(() => {});
      vi.spyOn(console, 'warn').mockImplementation(() => {});
    });

    afterEach(() => {
      vi.restoreAllMocks();
    });

    it('should format valid timestamps correctly', () => {
      const date = new Date('2023-01-01T14:30:00');
      const formatted = formatTimestamp(date.toISOString());
      expect(formatted).toMatch(/\d{1,2}:\d{2}\s*(AM|PM)/i);
    });

    it('should return empty string for invalid timestamps', () => {
      expect(formatTimestamp('')).toBe('');
      expect(formatTimestamp(null)).toBe('');
      expect(formatTimestamp(undefined)).toBe('');
    });

    it('should handle edge cases', () => {
      expect(formatTimestamp('invalid-date')).toBe('');
      expect(formatTimestamp('2023-13-45')).toBe('');
    });
  });

  describe('sanitizeMessage', () => {
    it('should trim whitespace and limit length to 1000 characters', () => {
      const longMessage = 'a'.repeat(1500);
      const sanitized = sanitizeMessage(longMessage);
      expect(sanitized.length).toBe(1000);
    });

    it('should trim whitespace', () => {
      expect(sanitizeMessage('  hello  ')).toBe('hello');
      expect(sanitizeMessage('\n\t hello \n\t')).toBe('hello');
    });

    it('should return empty string for null/undefined', () => {
      expect(sanitizeMessage(null)).toBe('');
      expect(sanitizeMessage(undefined)).toBe('');
      expect(sanitizeMessage('')).toBe('');
    });

    it('should handle normal messages correctly', () => {
      const normalMessage = 'Hello, this is a normal message!';
      expect(sanitizeMessage(normalMessage)).toBe(normalMessage);
    });
  });

  describe('createUserHash', () => {
    it('should create consistent hash for same input', () => {
      const userId = 'user123';
      const hash1 = createUserHash(userId);
      const hash2 = createUserHash(userId);
      expect(hash1).toBe(hash2);
    });

    it('should create different hashes for different inputs', () => {
      const hash1 = createUserHash('user1');
      const hash2 = createUserHash('user2');
      expect(hash1).not.toBe(hash2);
    });

    it('should return 0 for null/undefined/empty input', () => {
      expect(createUserHash(null)).toBe(0);
      expect(createUserHash(undefined)).toBe(0);
      expect(createUserHash('')).toBe(0);
    });

    it('should handle various input types', () => {
      expect(typeof createUserHash('test')).toBe('number');
      expect(createUserHash('test')).toBeGreaterThan(0);
    });
  });

  describe('isValidRoomName', () => {
    it('should return true for valid room names', () => {
      expect(isValidRoomName('General')).toBe(true);
      expect(isValidRoomName('a')).toBe(true);
      expect(isValidRoomName('a'.repeat(50))).toBe(true);
    });

    it('should return false for invalid room names', () => {
      expect(isValidRoomName('')).toBe(false);
      expect(isValidRoomName('  ')).toBe(false);
      expect(isValidRoomName(null)).toBe(false);
      expect(isValidRoomName(undefined)).toBe(false);
      expect(isValidRoomName('a'.repeat(51))).toBe(false);
    });

    it('should trim whitespace before validation', () => {
      expect(isValidRoomName('  Valid Name  ')).toBe(true);
      expect(isValidRoomName('   ')).toBe(false);
    });
  });

  describe('logger', () => {
    beforeEach(() => {
      vi.spyOn(console, 'debug').mockImplementation(() => {});
      vi.spyOn(console, 'info').mockImplementation(() => {});
      vi.spyOn(console, 'warn').mockImplementation(() => {});
      vi.spyOn(console, 'error').mockImplementation(() => {});
    });

    afterEach(() => {
      vi.restoreAllMocks();
    });

    it('should call console.debug for debug logs', () => {
      logger.debug('test message');
      expect(console.debug).toHaveBeenCalledWith('[DEBUG]', 'test message');
    });

    it('should call console.info for info logs', () => {
      logger.info('test message');
      expect(console.info).toHaveBeenCalledWith('[INFO]', 'test message');
    });

    it('should call console.warn for warn logs', () => {
      logger.warn('test message');
      expect(console.warn).toHaveBeenCalledWith('[WARN]', 'test message');
    });

    it('should call console.error for error logs', () => {
      logger.error('test message');
      expect(console.error).toHaveBeenCalledWith('[ERROR]', 'test message');
    });

    it('should handle multiple arguments', () => {
      logger.info('message', 'arg1', 'arg2');
      expect(console.info).toHaveBeenCalledWith('[INFO]', 'message', 'arg1', 'arg2');
    });
  });
});