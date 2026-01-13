const bcrypt = require('bcryptjs')
const jwt = require('jsonwebtoken')

// Mock the dependencies
jest.mock('bcryptjs')
jest.mock('jsonwebtoken')

// Import functions to test (these would be extracted from server.js in a real scenario)
const SECRET_KEY = process.env.JWT_SECRET || 'test-secret-key'

// These functions would normally be imported from a separate auth module
const generateTokens = (userId) => {
  const accessToken = jwt.sign(
    { userId, type: 'access' },
    SECRET_KEY,
    { expiresIn: '15m' }
  )
  
  const refreshToken = jwt.sign(
    { userId, type: 'refresh' },
    SECRET_KEY,
    { expiresIn: '7d' }
  )
  
  return { accessToken, refreshToken }
}

const validatePassword = async (password, hashedPassword) => {
  return await bcrypt.compare(password, hashedPassword)
}

const hashPassword = async (password) => {
  const salt = await bcrypt.genSalt(12)
  return await bcrypt.hash(password, salt)
}

describe('Authentication Functions', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('generateTokens', () => {
    it('should generate valid access and refresh tokens', () => {
      const userId = 'test-user-id'
      const mockAccessToken = 'mock-access-token'
      const mockRefreshToken = 'mock-refresh-token'
      
      jwt.sign.mockImplementationOnce(() => mockAccessToken)
      jwt.sign.mockImplementationOnce(() => mockRefreshToken)
      
      const tokens = generateTokens(userId)
      
      expect(tokens).toEqual({
        accessToken: mockAccessToken,
        refreshToken: mockRefreshToken
      })
      
      expect(jwt.sign).toHaveBeenCalledTimes(2)
      expect(jwt.sign).toHaveBeenNthCalledWith(1, 
        { userId, type: 'access' },
        SECRET_KEY,
        { expiresIn: '15m' }
      )
      expect(jwt.sign).toHaveBeenNthCalledWith(2,
        { userId, type: 'refresh' },
        SECRET_KEY,
        { expiresIn: '7d' }
      )
    })
  })

  describe('validatePassword', () => {
    it('should return true for correct password', async () => {
      const password = 'test-password'
      const hashedPassword = 'hashed-password'
      bcrypt.compare.mockResolvedValue(true)
      
      const result = await validatePassword(password, hashedPassword)
      
      expect(result).toBe(true)
      expect(bcrypt.compare).toHaveBeenCalledWith(password, hashedPassword)
    })

    it('should return false for incorrect password', async () => {
      const password = 'wrong-password'
      const hashedPassword = 'hashed-password'
      bcrypt.compare.mockResolvedValue(false)
      
      const result = await validatePassword(password, hashedPassword)
      
      expect(result).toBe(false)
    })
  })

  describe('hashPassword', () => {
    it('should hash password with salt', async () => {
      const password = 'test-password'
      const mockSalt = 'mock-salt'
      const mockHashedPassword = 'mock-hashed-password'
      
      bcrypt.genSalt.mockResolvedValue(mockSalt)
      bcrypt.hash.mockResolvedValue(mockHashedPassword)
      
      const result = await hashPassword(password)
      
      expect(result).toBe(mockHashedPassword)
      expect(bcrypt.genSalt).toHaveBeenCalledWith(12)
      expect(bcrypt.hash).toHaveBeenCalledWith(password, mockSalt)
    })
  })
})