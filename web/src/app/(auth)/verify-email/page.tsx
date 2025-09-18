import VerifyEmailForm from '@/components/auth/VerifyEmailForm'
import Link from 'next/link'
import { Suspense } from 'react'

// VerifyEmailForm uses useSearchParams, which requires Suspense boundary in app directory
function VerifyEmailContent() {
  return <VerifyEmailForm />
}

export default function VerifyEmailPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <Link href="/" className="flex justify-center">
          <h1 className="text-3xl font-bold text-blue-600">InstaBids</h1>
        </Link>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Verify your email
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <Suspense fallback={
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading...</p>
            </div>
          }>
            <VerifyEmailContent />
          </Suspense>
        </div>
      </div>
    </div>
  )
}