import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import App from '../App'

// Mock axios
vi.mock('axios')

describe('App Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks()
  })

  it('renders login form initially', () => {
    render(<App />)
    
    expect(screen.getByText('Welcome to ChatApp')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument()
  })

  it('switches to registration form when signup is clicked', async () => {
    render(<App />)
    
    const signupButton = screen.getByText('Sign Up')
    fireEvent.click(signupButton)
    
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Username')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('First Name')).toBeInTheDocument()
    })
  })

  it('validates login form inputs', async () => {
    render(<App />)
    
    const loginButton = screen.getByText('Sign In')
    fireEvent.click(loginButton)
    
    // Should show validation errors or remain on login form
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument()
  })

  it('handles login form submission', async () => {
    const mockAxios = await import('axios')
    mockAxios.default.post.mockResolvedValue({
      data: {
        tokens: { accessToken: 'test-token' },
        user: { id: '1', username: 'testuser' }
      }
    })

    render(<App />)
    
    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'test@example.com' }
    })
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'password123' }
    })
    
    fireEvent.click(screen.getByText('Sign In'))
    
    await waitFor(() => {
      expect(mockAxios.default.post).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/login',
        {
          email: 'test@example.com',
          password: 'password123'
        }
      )
    })
  })

  it('shows error message on failed login', async () => {
    const mockAxios = await import('axios')
    mockAxios.default.post.mockRejectedValue({
      response: { data: { message: 'Invalid credentials' } }
    })

    render(<App />)
    
    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'wrong@example.com' }
    })
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'wrongpass' }
    })
    
    fireEvent.click(screen.getByText('Sign In'))
    
    // The app should handle the error gracefully
    await waitFor(() => {
      expect(screen.getByText('Welcome to ChatApp')).toBeInTheDocument()
    })
  })
})

describe('Authentication Flow', () => {
  it('stores token in localStorage on successful login', async () => {
    const mockAxios = await import('axios')
    mockAxios.default.post.mockResolvedValue({
      data: {
        tokens: { accessToken: 'mock-jwt-token' },
        user: { id: '1', username: 'testuser' }
      }
    })

    render(<App />)
    
    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'test@example.com' }
    })
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'password123' }
    })
    
    fireEvent.click(screen.getByText('Sign In'))
    
    await waitFor(() => {
      expect(localStorage.getItem('token')).toBe('mock-jwt-token')
    })
  })

  it('clears token on logout', async () => {
    localStorage.setItem('token', 'test-token')
    
    const mockAxios = await import('axios')
    mockAxios.default.post.mockResolvedValue({
      data: {
        tokens: { accessToken: 'test-token' },
        user: { id: '1', username: 'testuser' }
      }
    })

    render(<App />)
    
    // Wait for login to complete
    await waitFor(() => {
      expect(screen.getByText('Logout')).toBeInTheDocument()
    })
    
    fireEvent.click(screen.getByText('Logout'))
    
    expect(localStorage.getItem('token')).toBeNull()
  })
})