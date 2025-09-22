'use client'

import { useEffect, useRef, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import Link from 'next/link'

export default function VerifyEmailForm() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const token = searchParams.get('token')
  const emailParam = searchParams.get('email') ?? ''
  const verificationKey = token ? `${apiUrl}::${token}` : null

  const [status, setStatus] = useState<'verifying' | 'success' | 'error' | 'resent'>(() =>
    token ? 'verifying' : 'error'
  )
  const [error, setError] = useState<string | null>(() =>
    token ? null : 'Verification token is missing'
  )
  const [email, setEmail] = useState(() => emailParam)
  const [isResending, setIsResending] = useState(false)
  const [canResend, setCanResend] = useState(() => Boolean(emailParam))
  const lastVerificationKeyRef = useRef<string | null>(null)

  useEffect(() => {
    setEmail(emailParam)
    setCanResend((previous) => previous || Boolean(emailParam))

    if (!token) {
      setStatus('error')
      setError('Verification token is missing')
      lastVerificationKeyRef.current = null
      return
    }

    if (lastVerificationKeyRef.current === verificationKey) {
      return
    }

    lastVerificationKeyRef.current = verificationKey
    setStatus('verifying')
    setError(null)
    verifyEmail(token)
  }, [token, emailParam, apiUrl, verificationKey])

  async function verifyEmail(token: string) {
    try {
      const response = await fetch(`${apiUrl}/api/auth/verify-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
      })

      if (!response || !response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Verification failed')
      }

      setStatus('success')
      setTimeout(() => {
        router.push('/login')
      }, 3000)
    } catch (err) {
      setStatus('error')
      setError((err as Error).message || 'Verification failed')
      lastVerificationKeyRef.current = null
    }
  }

  async function resendVerification() {
    if (!email) {
      setError('Email address is required')
      return
    }

    setIsResending(true)
    setError(null)
    try {
      const response = await fetch(`${apiUrl}/api/auth/resend-verification`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      })

      if (!response || !response.ok) {
        const errorData = response?.json ? await response.json() : null
        throw new Error(errorData?.detail || 'Failed to resend verification')
      }

      setStatus('resent')
    } catch (err) {
      setError((err as Error).message || 'Failed to resend verification')
    } finally {
      setIsResending(false)
    }
  }

  if (status === 'verifying') {
    return (
      <div className="w-full max-w-md mx-auto text-center" role="status" aria-live="polite">
        <div
          className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"
          aria-hidden="true"
        ></div>
        <p className="mt-4 text-gray-600">Verifying your email address...</p>
      </div>
    )
  }

  if (status === 'success') {
    return (
      <div className="w-full max-w-md mx-auto">
        <div className="rounded-md bg-green-50 p-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-8 w-8 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-medium text-green-800">
                Email verified successfully!
              </h3>
              <div className="mt-2 text-sm text-green-700">
                <p>Your email has been verified. You&apos;ll be redirected to login in a moment...</p>
              </div>
              <div className="mt-4">
                <Link href="/login" className="text-sm font-medium text-green-600 hover:text-green-500">
                  Go to login now →
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (status === 'resent') {
    return (
      <div className="w-full max-w-md mx-auto">
        <div className="rounded-md bg-blue-50 p-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-8 w-8 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-medium text-blue-800">
                Verification email sent!
              </h3>
              <div className="mt-2 text-sm text-blue-700">
                <p>We&apos;ve sent a new verification link to {email}. Please check your inbox.</p>
              </div>
              <div className="mt-4">
                <Link href="/login" className="text-sm font-medium text-blue-600 hover:text-blue-500">
                  Back to login →
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Error state with resend option
  return (
    <div className="w-full max-w-md mx-auto">
      <div className="rounded-md bg-red-50 p-6">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-8 w-8 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3 flex-1">
            <h3 className="text-lg font-medium text-red-800">
              Verification failed
            </h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{error || 'The verification link is invalid or has expired.'}</p>
            </div>
            
            {canResend && (
              <div className="mt-4 space-y-3">
                <div>
                  <label htmlFor="resend-email" className="block text-sm font-medium text-gray-700">
                    Email address
                  </label>
                  <input
                    id="resend-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    placeholder="you@example.com"
                  />
                </div>

                <button
                  onClick={resendVerification}
                  disabled={isResending || !email.trim().length}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isResending ? 'Sending...' : 'Resend verification email'}
                </button>
              </div>
            )}

            <div className="mt-4">
              <Link href="/login" className="text-sm font-medium text-red-600 hover:text-red-500">
                Back to login →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}