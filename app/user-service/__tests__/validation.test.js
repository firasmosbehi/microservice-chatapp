const Joi = require('joi')

// Validation schemas that would be extracted from server.js
const registerSchema = Joi.object({
  username: Joi.string().min(3).max(30).required(),
  email: Joi.string().email().required(),
  password: Joi.string().min(6).required(),
  firstName: Joi.string().min(1).max(50).required(),
  lastName: Joi.string().min(1).max(50).required()
})

const loginSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().required()
})

const profileSchema = Joi.object({
  firstName: Joi.string().min(1).max(50),
  lastName: Joi.string().min(1).max(50),
  avatar: Joi.string().uri().optional()
})

const passwordChangeSchema = Joi.object({
  currentPassword: Joi.string().required(),
  newPassword: Joi.string().min(6).required()
})

describe('Validation Schemas', () => {
  describe('registerSchema', () => {
    it('should validate correct registration data', () => {
      const validData = {
        username: 'testuser',
        email: 'test@example.com',
        password: 'password123',
        firstName: 'John',
        lastName: 'Doe'
      }
      
      const { error } = registerSchema.validate(validData)
      expect(error).toBeUndefined()
    })

    it('should reject invalid username', () => {
      const invalidData = {
        username: 'ab', // too short
        email: 'test@example.com',
        password: 'password123',
        firstName: 'John',
        lastName: 'Doe'
      }
      
      const { error } = registerSchema.validate(invalidData)
      expect(error).toBeDefined()
      expect(error.details[0].path[0]).toBe('username')
    })

    it('should reject invalid email', () => {
      const invalidData = {
        username: 'testuser',
        email: 'invalid-email',
        password: 'password123',
        firstName: 'John',
        lastName: 'Doe'
      }
      
      const { error } = registerSchema.validate(invalidData)
      expect(error).toBeDefined()
      expect(error.details[0].path[0]).toBe('email')
    })

    it('should reject short password', () => {
      const invalidData = {
        username: 'testuser',
        email: 'test@example.com',
        password: '123', // too short
        firstName: 'John',
        lastName: 'Doe'
      }
      
      const { error } = registerSchema.validate(invalidData)
      expect(error).toBeDefined()
      expect(error.details[0].path[0]).toBe('password')
    })
  })

  describe('loginSchema', () => {
    it('should validate correct login data', () => {
      const validData = {
        email: 'test@example.com',
        password: 'password123'
      }
      
      const { error } = loginSchema.validate(validData)
      expect(error).toBeUndefined()
    })

    it('should reject missing email', () => {
      const invalidData = {
        password: 'password123'
      }
      
      const { error } = loginSchema.validate(invalidData)
      expect(error).toBeDefined()
      expect(error.details[0].path[0]).toBe('email')
    })

    it('should reject invalid email format', () => {
      const invalidData = {
        email: 'not-an-email',
        password: 'password123'
      }
      
      const { error } = loginSchema.validate(invalidData)
      expect(error).toBeDefined()
    })
  })

  describe('profileSchema', () => {
    it('should validate correct profile update data', () => {
      const validData = {
        firstName: 'Jane',
        lastName: 'Smith',
        avatar: 'https://example.com/avatar.jpg'
      }
      
      const { error } = profileSchema.validate(validData)
      expect(error).toBeUndefined()
    })

    it('should allow partial profile updates', () => {
      const validData = {
        firstName: 'Jane'
        // lastName and avatar are optional
      }
      
      const { error } = profileSchema.validate(validData)
      expect(error).toBeUndefined()
    })

    it('should reject invalid URI for avatar', () => {
      const invalidData = {
        firstName: 'Jane',
        avatar: 'not-a-valid-uri'
      }
      
      const { error } = profileSchema.validate(invalidData)
      expect(error).toBeDefined()
      expect(error.details[0].path[0]).toBe('avatar')
    })
  })

  describe('passwordChangeSchema', () => {
    it('should validate correct password change data', () => {
      const validData = {
        currentPassword: 'oldpassword123',
        newPassword: 'newpassword456'
      }
      
      const { error } = passwordChangeSchema.validate(validData)
      expect(error).toBeUndefined()
    })

    it('should reject short new password', () => {
      const invalidData = {
        currentPassword: 'oldpassword123',
        newPassword: '123' // too short
      }
      
      const { error } = passwordChangeSchema.validate(invalidData)
      expect(error).toBeDefined()
      expect(error.details[0].path[0]).toBe('newPassword')
    })

    it('should reject missing current password', () => {
      const invalidData = {
        newPassword: 'newpassword456'
      }
      
      const { error } = passwordChangeSchema.validate(invalidData)
      expect(error).toBeDefined()
      expect(error.details[0].path[0]).toBe('currentPassword')
    })
  })
})