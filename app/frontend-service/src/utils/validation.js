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
  return name && name.trim().length >= 1 && name.trim().length <= 50
}