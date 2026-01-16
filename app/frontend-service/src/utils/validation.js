// Utility functions for the chat application

export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export const validatePassword = (password) => {
  return password.length >= 6
}

export const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  // Check if date is valid
  if (isNaN(date.getTime())) return ''
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export const sanitizeMessage = (message) => {
  if (!message) return ''
  return message.trim().substring(0, 1000) // Limit message length
}

export const createUserHash = (userId) => {
  if (!userId) return 0
  return userId.split('').reduce((acc, char) => {
    return acc + char.charCodeAt(0)
  }, 0)
}

export const isValidRoomName = (name) => {
  if (typeof name !== 'string') return false
  const trimmed = name.trim()
  return trimmed.length >= 1 && trimmed.length <= 50
}

// Logging utility to handle different log levels
export const logger = {
  debug: (...args) => {
    // Debug logs only in development
    if (import.meta.env?.DEV) {
      console.debug('[DEBUG]', ...args)
    }
  },
  info: (...args) => {
    console.info('[INFO]', ...args)
  },
  warn: (...args) => {
    console.warn('[WARN]', ...args)
  },
  error: (...args) => {
    console.error('[ERROR]', ...args)
  }
}