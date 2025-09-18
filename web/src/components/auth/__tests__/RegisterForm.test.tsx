/**
 * @jest-environment jsdom
 */
import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import RegisterForm from '../RegisterForm'

// Mock the AuthContext
const mockRegister = jest.fn()
jest.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({
    register: mockRegister,
  }),
}))

// Mock Next.js Link
jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  )
})

describe('RegisterForm', () => {
  beforeEach(() => {
    mockRegister.mockClear()
    mockRegister.mockResolvedValue({})
  })

  it('renders all form fields', () => {
    render(<RegisterForm />)
    
    // Check for user type options
    expect(screen.getByText('Property Manager')).toBeInTheDocument()
    expect(screen.getByText('Contractor')).toBeInTheDocument()
    expect(screen.getByText('Tenant')).toBeInTheDocument()
    
    // Check for form fields
    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/phone/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument()
  })

  it('shows organization field for property managers', async () => {
    const user = userEvent.setup()
    render(<RegisterForm />)
    
    // Property manager should be selected by default
    expect(screen.getByLabelText(/organization name/i)).toBeInTheDocument()
    
    // Switch to contractor
    await user.click(screen.getByLabelText('Contractor'))
    
    // Organization field should be hidden
    expect(screen.queryByLabelText(/organization name/i)).not.toBeInTheDocument()
    
    // Switch back to property manager
    await user.click(screen.getByLabelText('Property Manager'))
    
    // Organization field should be visible again
    expect(screen.getByLabelText(/organization name/i)).toBeInTheDocument()
  })

  it('validates required fields', async () => {
    const user = userEvent.setup()
    render(<RegisterForm />)
    
    // Try to submit empty form
    await user.click(screen.getByRole('button', { name: /create account/i }))
    
    // Should show validation errors
    await waitFor(() => {
      expect(screen.getByText(/name must be at least 2 characters/i)).toBeInTheDocument()
      expect(screen.getByText(/invalid email address/i)).toBeInTheDocument()
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument()
    })
  })

  it('validates email format', async () => {
    const user = userEvent.setup()
    render(<RegisterForm />)
    
    const emailInput = screen.getByLabelText(/email/i)
    await user.type(emailInput, 'invalid-email')
    await user.tab() // Trigger validation
    
    await waitFor(() => {
      expect(screen.getByText(/invalid email address/i)).toBeInTheDocument()
    })
  })

  it('validates password requirements', async () => {
    const user = userEvent.setup()
    render(<RegisterForm />)
    
    const passwordInput = screen.getByLabelText(/^password$/i)
    
    // Test weak password
    await user.type(passwordInput, 'weak')
    await user.tab()
    
    await waitFor(() => {
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument()
    })
    
    // Clear and test password without uppercase
    await user.clear(passwordInput)
    await user.type(passwordInput, 'lowercase123')
    await user.tab()
    
    await waitFor(() => {
      expect(screen.getByText(/password must contain at least one uppercase letter/i)).toBeInTheDocument()
    })
    
    // Clear and test password without lowercase
    await user.clear(passwordInput)
    await user.type(passwordInput, 'UPPERCASE123')
    await user.tab()
    
    await waitFor(() => {
      expect(screen.getByText(/password must contain at least one lowercase letter/i)).toBeInTheDocument()
    })
    
    // Clear and test password without number
    await user.clear(passwordInput)
    await user.type(passwordInput, 'Password')
    await user.tab()
    
    await waitFor(() => {
      expect(screen.getByText(/password must contain at least one number/i)).toBeInTheDocument()
    })
  })

  it('validates password confirmation', async () => {
    const user = userEvent.setup()
    render(<RegisterForm />)
    
    const passwordInput = screen.getByLabelText(/^password$/i)
    const confirmInput = screen.getByLabelText(/confirm password/i)
    
    await user.type(passwordInput, 'Password123!')
    await user.type(confirmInput, 'DifferentPassword123!')
    await user.tab()
    
    await waitFor(() => {
      expect(screen.getByText(/passwords don't match/i)).toBeInTheDocument()
    })
  })

  it('submits form with valid data', async () => {
    const user = userEvent.setup()
    render(<RegisterForm />)
    
    // Fill in valid form data
    await user.type(screen.getByLabelText(/full name/i), 'Test User')
    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/organization name/i), 'Test Org')
    await user.type(screen.getByLabelText(/phone/i), '+1234567890')
    await user.type(screen.getByLabelText(/^password$/i), 'Password123!')
    await user.type(screen.getByLabelText(/confirm password/i), 'Password123!')
    
    // Submit form
    await user.click(screen.getByRole('button', { name: /create account/i }))
    
    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'Password123!',
        full_name: 'Test User',
        user_type: 'property_manager',
        phone: '+1234567890',
        organization_name: 'Test Org'
      })
    })
  })

  it('handles registration errors', async () => {
    const user = userEvent.setup()
    mockRegister.mockRejectedValueOnce(new Error('Registration failed'))
    
    render(<RegisterForm />)
    
    // Fill in valid form data
    await user.type(screen.getByLabelText(/full name/i), 'Test User')
    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/^password$/i), 'Password123!')
    await user.type(screen.getByLabelText(/confirm password/i), 'Password123!')
    
    // Submit form
    await user.click(screen.getByRole('button', { name: /create account/i }))
    
    await waitFor(() => {
      expect(screen.getByText(/registration failed/i)).toBeInTheDocument()
    })
  })

  it('shows loading state during submission', async () => {
    const user = userEvent.setup()
    let resolveRegister: () => void
    mockRegister.mockImplementationOnce(() => new Promise(resolve => {
      resolveRegister = resolve
    }))
    
    render(<RegisterForm />)
    
    // Fill in valid form data
    await user.type(screen.getByLabelText(/full name/i), 'Test User')
    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/^password$/i), 'Password123!')
    await user.type(screen.getByLabelText(/confirm password/i), 'Password123!')
    
    // Submit form
    await user.click(screen.getByRole('button', { name: /create account/i }))
    
    // Should show loading state
    expect(screen.getByText(/creating account/i)).toBeInTheDocument()
    
    // Resolve the promise
    resolveRegister!()
    
    await waitFor(() => {
      expect(screen.getByText(/create account/i)).toBeInTheDocument()
    })
  })

  it('disables submit button during loading', async () => {
    const user = userEvent.setup()
    let resolveRegister: () => void
    mockRegister.mockImplementationOnce(() => new Promise(resolve => {
      resolveRegister = resolve
    }))
    
    render(<RegisterForm />)
    
    // Fill in valid form data
    await user.type(screen.getByLabelText(/full name/i), 'Test User')
    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/^password$/i), 'Password123!')
    await user.type(screen.getByLabelText(/confirm password/i), 'Password123!')
    
    const submitButton = screen.getByRole('button', { name: /create account/i })
    
    // Submit form
    await user.click(submitButton)
    
    // Button should be disabled
    expect(submitButton).toBeDisabled()
    
    // Resolve the promise
    resolveRegister!()
    
    await waitFor(() => {
      expect(submitButton).not.toBeDisabled()
    })
  })

  it('includes sign in link', () => {
    render(<RegisterForm />)
    
    const signInLink = screen.getByRole('link', { name: /sign in/i })
    expect(signInLink).toBeInTheDocument()
    expect(signInLink).toHaveAttribute('href', '/login')
  })

  it('handles different user types correctly', async () => {
    const user = userEvent.setup()
    render(<RegisterForm />)
    
    // Test contractor selection
    await user.click(screen.getByLabelText('Contractor'))
    
    // Fill in form data
    await user.type(screen.getByLabelText(/full name/i), 'Test Contractor')
    await user.type(screen.getByLabelText(/email/i), 'contractor@example.com')
    await user.type(screen.getByLabelText(/^password$/i), 'Password123!')
    await user.type(screen.getByLabelText(/confirm password/i), 'Password123!')
    
    // Submit form
    await user.click(screen.getByRole('button', { name: /create account/i }))
    
    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith({
        email: 'contractor@example.com',
        password: 'Password123!',
        full_name: 'Test Contractor',
        user_type: 'contractor',
        phone: ''
      })
    })
  })

  it('handles optional phone field correctly', async () => {
    const user = userEvent.setup()
    render(<RegisterForm />)
    
    // Fill in form without phone
    await user.type(screen.getByLabelText(/full name/i), 'Test User')
    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/^password$/i), 'Password123!')
    await user.type(screen.getByLabelText(/confirm password/i), 'Password123!')
    
    // Submit form
    await user.click(screen.getByRole('button', { name: /create account/i }))
    
    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith(
        expect.objectContaining({
          phone: ''
        })
      )
    })
  })
})