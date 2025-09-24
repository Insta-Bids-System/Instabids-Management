'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useEffect } from 'react'

export default function PropertyManagerDashboard() {
  const { user, logout } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // Redirect if not a property manager
    if (user && user.user_type !== 'property_manager') {
      router.push('/dashboard')
    }
  }, [user, router])

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">InstaBids - Property Manager</h1>
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
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-xl p-8 mb-8">
          <h2 className="text-3xl font-bold text-white mb-4">
            Property Management Dashboard
          </h2>
          <p className="text-blue-100 text-lg mb-6">
            Manage your properties and maintenance projects efficiently
          </p>
          <Link
            href="/projects/new"
            className="inline-flex items-center px-4 py-2 border border-transparent text-base font-medium rounded-md text-indigo-600 bg-white hover:bg-blue-50"
          >
            Create New Project
          </Link>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Properties</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">0</p>
            <Link href="#" className="text-sm text-blue-600 hover:text-blue-500 mt-1">
              Add property →
            </Link>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Active Projects</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">0</p>
            <p className="text-sm text-green-600 mt-1">All on track</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Pending Quotes</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">0</p>
            <p className="text-sm text-orange-600 mt-1">Awaiting review</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">This Month</h3>
            <p className="text-2xl font-bold text-gray-900 mt-2">$0</p>
            <p className="text-sm text-gray-500 mt-1">Total spend</p>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Properties Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h3 className="text-lg font-medium text-gray-900">Your Properties</h3>
                <button className="text-sm text-blue-600 hover:text-blue-500">
                  Add Property
                </button>
              </div>
              <div className="p-6">
                <div className="text-center py-12">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                  <h4 className="mt-2 text-sm font-medium text-gray-900">No properties yet</h4>
                  <p className="mt-1 text-sm text-gray-500">
                    Add your properties to start managing maintenance
                  </p>
                  <button className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
                    Add Your First Property
                  </button>
                </div>
              </div>
            </div>

            {/* Recent Projects */}
            <div className="bg-white rounded-lg shadow mt-8">
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h3 className="text-lg font-medium text-gray-900">Recent Projects</h3>
                <Link
                  href="/projects/new"
                  className="text-sm text-blue-600 hover:text-blue-500"
                >
                  New Project
                </Link>
              </div>
              <div className="p-6">
                <div className="text-center py-8">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                  <h4 className="mt-2 text-sm font-medium text-gray-900">No projects yet</h4>
                  <p className="mt-1 text-sm text-gray-500">
                    Create a project to get quotes from contractors
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
              </div>
              <div className="p-6 space-y-3">
                <Link
                  href="/projects/new"
                  className="w-full flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  Create New Project
                </Link>
                <button className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                  Add Property
                </button>
                <button className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                  Invite Contractor
                </button>
                <button className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                  View Reports
                </button>
              </div>
            </div>

            {/* SmartScope AI */}
            <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-lg shadow p-6">
              <div className="flex items-center mb-3">
                <svg className="h-6 w-6 text-purple-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                <h3 className="text-lg font-medium text-gray-900">SmartScope AI</h3>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                Upload photos and let AI analyze your maintenance needs automatically
              </p>
              <button className="text-sm font-medium text-purple-600 hover:text-purple-500">
                Learn more →
              </button>
            </div>

            {/* Help Section */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Need Help?</h3>
              <ul className="space-y-2">
                <li>
                  <a href="#" className="text-sm text-blue-600 hover:text-blue-500">
                    Getting Started Guide
                  </a>
                </li>
                <li>
                  <a href="#" className="text-sm text-blue-600 hover:text-blue-500">
                    How to Create Projects
                  </a>
                </li>
                <li>
                  <a href="#" className="text-sm text-blue-600 hover:text-blue-500">
                    Managing Contractors
                  </a>
                </li>
                <li>
                  <a href="#" className="text-sm text-blue-600 hover:text-blue-500">
                    Contact Support
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}