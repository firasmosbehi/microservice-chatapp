const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const validator = require('validator');

// Password hashing utilities
async function hashPassword(password) {
  const saltRounds = 12;
  return await bcrypt.hash(password, saltRounds);
}

async function comparePasswords(password, hashedPassword) {
  return await bcrypt.compare(password, hashedPassword);
}

// JWT token utilities
function generateTokens(userId) {
  const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';

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

  return { accessToken, refreshToken };
}

function verifyToken(token) {
  try {
    const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';
    return jwt.verify(token, JWT_SECRET);
  } catch (error) {
    return null;
  }
}

// Validation utilities
function validateEmail(email) {
  return validator.isEmail(email);
}

function validatePassword(password) {
  // Password requirements: 6-100 characters
  if (!password || password.length < 6 || password.length > 100) {
    return false;
  }
  return true;
}

// Export all utilities
module.exports = {
  hashPassword,
  comparePasswords,
  generateTokens,
  verifyToken,
  validateEmail,
  validatePassword
};
