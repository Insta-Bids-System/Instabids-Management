/**
 * @jest-environment jsdom
 */
import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import VerifyEmailForm from '../VerifyEmailForm'

// Mock Next.js navigation
const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  useSearchParams: jest.fn(),
  useRouter: () => ({
    push: mockPush,
  }),
}))

// Mock fetch
global.fetch = jest.fn()

describe('VerifyEmailForm', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockPush.mockClear()
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000'
  })

  it('shows verifying state initially with token', () => {
    const mockSearchParams = {
      get: jest.fn((key) => {
        if (key === 'token') return 'test-token'
        if (key === 'email') return 'test@example.com'
        return null
      })
    }
    
    require('next/navigation').useSearchParams.mockReturnValue(mockSearchParams)
    
    render(<VerifyEmailForm />)
    
    expect(screen.getByText(/verifying your email address/i)).toBeInTheDocument()
    expect(screen.getByRole('status')).toBeInTheDocument() // Loading spinner
  })

  it('shows error when token is missing', () => {
    const mockSearchParams = {
      get: jest.fn(() => null)
    }
    
    require('next/navigation').useSearchParams.mockReturnValue(mockSearchParams)
    
    render(<VerifyEmailForm />)
    
    expect(screen.getByText(/verification failed/i)).toBeInTheDocument()
    expect(screen.getByText(/verification token is missing/i)).toBeInTheDocument()
  })

  it('calls verification API with token', async () => {
    const mockSearchParams = {
      get: jest.fn((key) => {
        if (key === 'token') return 'test-token'
        return null
      })
    }
    
    require('next/navigation').useSearchParams.mockReturnValue(mockSearchParams)
    
    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ message: 'Email verified' })
    })
    
    render(<VerifyEmailForm />)
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/verify-email',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: 'test-token' })
        }
      )
    })
  })

  it('shows success state after successful verification', async () => {
    const mockSearchParams = {
      get: jest.fn((key) => {
        if (key === 'token') return 'test-token'
        return null
      })
    }
    
    require('next/navigation').useSearchParams.mockReturnValue(mockSearchParams)
    
    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ message: 'Email verified' })
    })
    
    render(<VerifyEmailForm />)
    
    await waitFor(() => {
      expect(screen.getByText(/email verified successfully/i)).toBeInTheDocument()
      expect(screen.getByText(/you'll be redirected to login/i)).toBeInTheDocument()
    })
    
    // Should redirect after 3 seconds
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/login')
    }, { timeout: 4000 })
  })

  it('shows error state when verification fails', async () => {
    const mockSearchParams = {
      get: jest.fn((key) => {
        if (key === 'token') return 'invalid-token'
        return null
      })
    }
    
    require('next/navigation').useSearchParams.mockReturnValue(mockSearchParams)
    
    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ detail: 'Invalid token' })
    })
    
    render(<VerifyEmailForm />)
    
    await waitFor(() => {
      expect(screen.getByText(/verification failed/i)).toBeInTheDocument()
      expect(screen.getByText(/invalid token/i)).toBeInTheDocument()
    })
  })

  it('handles network errors gracefully', async () => {
    const mockSearchParams = {
      get: jest.fn((key) => {
        if (key === 'token') return 'test-token'
        return null
      })
    }
    
    require('next/navigation').useSearchParams.mockReturnValue(mockSearchParams)
    
    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockRejectedValueOnce(new Error('Network error'))
    
    render(<VerifyEmailForm />)
    
    await waitFor(() => {
      expect(screen.getByText(/verification failed/i)).toBeInTheDocument()
      expect(screen.getByText(/network error/i)).toBeInTheDocument()
    })
  })

  it('allows resending verification email', async () => {
    const user = userEvent.setup()
    const mockSearchParams = {
      get: jest.fn((key) => {
        if (key === 'email') return 'test@example.com'
        return null
      })
    }
    
    require('next/navigation').useSearchParams.mockReturnValue(mockSearchParams)
    
    render(<VerifyEmailForm />)
    
    // Should be in error state (no token)
    expect(screen.getByText(/verification failed/i)).toBeInTheDocument()
    
    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ message: 'Verification email sent' })
    })
    
    // Click resend button
    await user.click(screen.getByRole('button', { name: /resend verification email/i }))
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/resend-verification',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: 'test@example.com' })
        }
      )
    })
    
    // Should show resent state
    await waitFor(() => {
      expect(screen.getByText(/verification email sent/i)).toBeInTheDocument()
      expect(screen.getByText(/we've sent a new verification link to test@example.com/i)).toBeInTheDocument()
    })
  })

  it('handles resend verification errors', async () => {
    const user = userEvent.setup()
    const mockSearchParams = {
      get: jest.fn((key) => {
        if (key === 'email') return 'test@example.com'
        return null
      })
    }
    
    require('next/navigation').useSearchParams.mockReturnValue(mockSearchParams)
    
    render(<VerifyEmailForm />)
    
    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ detail: 'Failed to send email' })
    })
    
    // Click resend button
    await user.click(screen.getByRole('button', { name: /resend verification email/i }))
    
    await waitFor(() => {
      expect(screen.getByText(/failed to send email/i)).toBeInTheDocument()
    })
  })

  it('allows editing email for resend', async () => {
    const user = userEvent.setup()
    const mockSearchParams = {
      get: jest.fn((key) => {
        if (key === 'email') return 'old@example.com'
        return null
      })
    }
    
    require('next/navigation').useSearchParams.mockReturnValue(mockSearchParams)
    
    render(<VerifyEmailForm />)
    
    const emailInput = screen.getByDisplayValue('old@example.com')
    
    // Change email
    await user.clear(emailInput)
    await user.type(emailInput, 'new@example.com')
    
    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ message: 'Verification email sent' })
    })
    
    // Click resend button
    await user.click(screen.getByRole('button', { name: /resend verification email/i }))
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/resend-verification',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: 'new@example.com' })
        }
      )
    })
  })

  it('validates email before resending', async () => {
    const user = userEvent.setup()
    const mockSearchParams = {
      get: jest.fn(() => null)
    }
    
    require('next/navigation').useSearchParams.mockReturnValue(mockSearchParams)
    
    render(<VerifyEmailForm />)
    
    // Should show resend option without email
    expect(screen.getByText(/verification failed/i)).toBeInTheDocument()
    
    // Try to resend without email (button should not be visible without email)
    expect(screen.queryByRole('button', { name: /resend verification email/i })).not.toBeInTheDocument()
  })

  it('shows loading state during resend', async () => {
    const user = userEvent.setup()
    const mockSearchParams = {
      get: jest.fn((key) => {
        if (key === 'email') return 'test@example.com'
        return null
      })
    }
    
    require('next/navigation').useSearchParams.mockReturnValue(mockSearchParams)
    
    let resolveResend: () => void
    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockImplementationOnce(() => new Promise(resolve => {
      resolveResend = resolve
    }))
    
    render(<VerifyEmailForm />)
    
    const resendButton = screen.getByRole('button', { name: /resend verification email/i })
    
    // Click resend button
    await user.click(resendButton)
    
    // Should show loading state
    expect(screen.getByText(/sending/i)).toBeInTheDocument()
    expect(resendButton).toBeDisabled()
    
    // Resolve the promise
    resolveResend!()
  })

  it('includes navigation links', () => {
    const mockSearchParams = {
      get: jest.fn(() => null)
    }
    
    require('next/navigation').useSearchParams.mockReturnValue(mockSearchParams)
    
    render(<VerifyEmailForm />)
    
    const loginLink = screen.getByRole('link', { name: /back to login/i })
    expect(loginLink).toBeInTheDocument()
    expect(loginLink).toHaveAttribute('href', '/login')
  })

  it('includes login link in success state', async () => {
    const mockSearchParams = {
      get: jest.fn((key) => {
        if (key === 'token') return 'test-token'
        return null
      })
    }
    
    require('next/navigation').useSearchParams.mockReturnValue(mockSearchParams)
    
    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ message: 'Email verified' })
    })
    
    render(<VerifyEmailForm />)
    
    await waitFor(() => {
      expect(screen.getByText(/email verified successfully/i)).toBeInTheDocument()
    })
    
    const loginLink = screen.getByRole('link', { name: /go to login now/i })
    expect(loginLink).toBeInTheDocument()
    expect(loginLink).toHaveAttribute('href', '/login')
  })

  it('uses correct API URL from environment', async () => {
    process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com'
    
    const mockSearchParams = {
      get: jest.fn((key) => {
        if (key === 'token') return 'test-token'
        return null
      })
    }
    
    require('next/navigation').useSearchParams.mockReturnValue(mockSearchParams)
    
    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ message: 'Email verified' })
    })
    
    render(<VerifyEmailForm />)
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/api/auth/verify-email',
        expect.any(Object)
      )
    })
  })
})