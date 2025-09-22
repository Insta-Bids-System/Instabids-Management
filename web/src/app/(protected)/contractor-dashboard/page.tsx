'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function ContractorDashboard() {
  const { user, logout } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // Redirect if not a contractor
    if (user && user.user_type !== 'contractor') {
      router.push('/dashboard')
    }
  }, [user, router])

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">InstaBids - Contractor Portal</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                {user?.full_name || user?.email}
              </span>
              <button
                onClick={logout}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="bg-blue-600 rounded-lg shadow-xl p-8 mb-8">
          <h2 className="text-3xl font-bold text-white mb-4">
            Welcome back, {user?.full_name || 'Contractor'}!
          </h2>
          <p className="text-blue-100 text-lg">
            View available projects and manage your bids
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Available Projects</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">0</p>
            <p className="text-sm text-green-600 mt-1">In your area</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Active Bids</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">0</p>
            <p className="text-sm text-blue-600 mt-1">Pending response</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Won Projects</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">0</p>
            <p className="text-sm text-purple-600 mt-1">This month</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Profile Status</h3>
            <p className="text-2xl font-bold text-orange-600 mt-2">Incomplete</p>
            <button className="text-sm text-blue-600 hover:text-blue-500 mt-1">
              Complete profile →
            </button>
          </div>
        </div>

        {/* Main Content Areas */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Available Projects */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                Available Projects Near You
              </h3>
            </div>
            <div className="p-6">
              <div className="text-center py-8">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-1 4h1m-1 4h1" />
                </svg>
                <h4 className="mt-2 text-sm font-medium text-gray-900">No projects available</h4>
                <p className="mt-1 text-sm text-gray-500">
                  New projects will appear here when property managers post them
                </p>
              </div>
            </div>
          </div>

          {/* Your Bids */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                Your Recent Bids
              </h3>
            </div>
            <div className="p-6">
              <div className="text-center py-8">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <h4 className="mt-2 text-sm font-medium text-gray-900">No bids submitted</h4>
                <p className="mt-1 text-sm text-gray-500">
                  Your bid history will appear here
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Profile Completion CTA */}
        <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-yellow-800">
                Complete your contractor profile
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>
                  Add your business details, licenses, insurance, and service areas to start receiving project invitations.
                </p>
              </div>
              <div className="mt-4">
                <button className="text-sm font-medium text-yellow-800 hover:text-yellow-700">
                  Complete profile now →
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}