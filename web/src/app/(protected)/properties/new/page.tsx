'use client';

import { useRouter } from 'next/navigation';
import PropertyForm from '@/components/properties/PropertyForm';
import { ArrowLeft } from 'lucide-react';

export default function NewPropertyPage() {
  const router = useRouter();

  const handleSuccess = () => {
    router.push('/properties');
  };

  const handleCancel = () => {
    router.back();
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button
          onClick={handleCancel}
          className="p-2 hover:bg-gray-100 rounded-lg transition"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Add New Property</h1>
          <p className="text-gray-600">Enter property details to add it to your portfolio</p>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <PropertyForm
          onSuccess={handleSuccess}
          onCancel={handleCancel}
        />
      </div>
    </div>
  );
}