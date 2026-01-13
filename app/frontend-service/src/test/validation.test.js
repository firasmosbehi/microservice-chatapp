import { describe, it, expect } from 'vitest'
import {
  validateEmail,
  validatePassword,
  formatTimestamp,
  sanitizeMessage,
  createUserHash,
  isValidRoomName
} from '../utils/validation'

describe('Validation Utilities', () => {
  describe('validateEmail', () => {
    it('returns true for valid emails', () => {
      expect(validateEmail('test@example.com')).toBe(true)
      expect(validateEmail('user.name@domain.co.uk')).toBe(true)
      expect(validateEmail('test+tag@example.org')).toBe(true)
    })

    it('returns false for invalid emails', () => {
      expect(validateEmail('invalid-email')).toBe(false)
      expect(validateEmail('test@')).toBe(false)
      expect(validateEmail('@example.com')).toBe(false)
      expect(validateEmail('test.example.com')).toBe(false)
      expect(validateEmail('')).toBe(false)
    })
  })

  describe('validatePassword', () => {
    it('returns true for valid passwords (6+ characters)', () => {
      expect(validatePassword('password')).toBe(true)
      expect(validatePassword('123456')).toBe(true)
      expect(validatePassword('a'.repeat(10))).toBe(true)
    })

    it('returns false for invalid passwords (< 6 characters)', () => {
      expect(validatePassword('')).toBe(false)
      expect(validatePassword('12345')).toBe(false)
      expect(validatePassword('abc')).toBe(false)
    })
  })

  describe('formatTimestamp', () => {
    it('formats valid timestamps correctly', () => {
      const timestamp = '2026-01-11T16:40:41.137799'
      const formatted = formatTimestamp(timestamp)
      expect(formatted).toMatch(/\d{1,2}:\d{2}/) // Matches HH:MM format
    })

    it('returns empty string for invalid timestamps', () => {
      expect(formatTimestamp(null)).toBe('')
      expect(formatTimestamp(undefined)).toBe('')
      expect(formatTimestamp('')).toBe('')
    })
  })

  describe('sanitizeMessage', () => {
    it('trims whitespace from messages', () => {
      expect(sanitizeMessage('  Hello world  ')).toBe('Hello world')
      expect(sanitizeMessage('\n\tHello\n\t')).toBe('Hello')
    })

    it('limits message length to 1000 characters', () => {
      const longMessage = 'a'.repeat(1500)
      const sanitized = sanitizeMessage(longMessage)
      expect(sanitized.length).toBe(1000)
    })

    it('handles edge cases', () => {
      expect(sanitizeMessage('')).toBe('')
      expect(sanitizeMessage(null)).toBe('')
      expect(sanitizeMessage(undefined)).toBe('')
    })
  })

  describe('createUserHash', () => {
    it('creates consistent hash values', () => {
      const userId = 'user123'
      const hash1 = createUserHash(userId)
      const hash2 = createUserHash(userId)
      expect(hash1).toBe(hash2)
    })

    it('returns 0 for invalid user IDs', () => {
      expect(createUserHash(null)).toBe(0)
      expect(createUserHash(undefined)).toBe(0)
      expect(createUserHash('')).toBe(0)
    })

    it('generates different hashes for different users', () => {
      const hash1 = createUserHash('user1')
      const hash2 = createUserHash('user2')
      expect(hash1).not.toBe(hash2)
    })
  })

  describe('isValidRoomName', () => {
    it('returns true for valid room names', () => {
      expect(isValidRoomName('General')).toBe(true)
      expect(isValidRoomName('Team Meeting')).toBe(true)
      expect(isValidRoomName('a')).toBe(true)
      expect(isValidRoomName('a'.repeat(50))).toBe(true)
    })

    it('returns false for invalid room names', () => {
      expect(isValidRoomName('')).toBe(false)
      expect(isValidRoomName('   ')).toBe(false)
      expect(isValidRoomName(null)).toBe(false)
      expect(isValidRoomName(undefined)).toBe(false)
      expect(isValidRoomName('a'.repeat(51))).toBe(false)
    })
  })
})