'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // Redirect to appropriate dashboard based on user type
    if (user) {
      if (user.user_type === 'contractor') {
        router.push('/contractor-dashboard')
      } else if (user.user_type === 'property_manager') {
        router.push('/pm-dashboard')
      }
    }
  }, [user, router])

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">InstaBids Management</h1>
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
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Welcome to your Dashboard
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-medium text-gray-900">User Info</h3>
                <dl className="mt-4 space-y-2">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Email</dt>
                    <dd className="text-sm text-gray-900">{user?.email}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Role</dt>
                    <dd className="text-sm text-gray-900 capitalize">
                      {user?.user_type?.replace('_', ' ')}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Verified</dt>
                    <dd className="text-sm text-gray-900">
                      {user?.email_verified ? '✓ Yes' : '✗ No'}
                    </dd>
                  </div>
                </dl>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-medium text-gray-900">Properties</h3>
                <p className="mt-4 text-sm text-gray-500">
                  No properties added yet
                </p>
                <button className="mt-4 text-sm text-blue-600 hover:text-blue-500">
                  Add your first property →
                </button>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-medium text-gray-900">Projects</h3>
                <p className="mt-4 text-sm text-gray-500">
                  No active projects
                </p>
                <button className="mt-4 text-sm text-blue-600 hover:text-blue-500">
                  Create a project →
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}