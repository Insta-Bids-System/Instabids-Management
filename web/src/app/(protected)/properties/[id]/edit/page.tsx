'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Property, PropertyFormData } from '@/packages/shared/src/types/property';
import { propertiesApi } from '@/api/properties';
import PropertyForm from '@/components/properties/PropertyForm';
import { ArrowLeft, Loader2 } from 'lucide-react';

interface EditPropertyPageProps {
  params: { id: string };
}

export default function EditPropertyPage({ params }: EditPropertyPageProps) {
  const router = useRouter();
  const [property, setProperty] = useState<Property | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProperty();
  }, [params.id]);

  const loadProperty = async () => {
    try {
      setLoading(true);
      const data = await propertiesApi.getProperty(params.id);
      setProperty(data);
      setError(null);
    } catch (err) {
      setError('Failed to load property details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSuccess = () => {
    router.push(`/properties/${params.id}`);
  };

  const handleCancel = () => {
    router.back();
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      </div>
    );
  }

  if (error || !property) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error || 'Property not found'}
        </div>
      </div>
    );
  }

  // Convert Property to PropertyFormData
  const initialData: PropertyFormData = {
    address: property.address,
    city: property.city,
    state: property.state,
    zip_code: property.zip_code,
    property_type: property.property_type,
    bedrooms: property.bedrooms,
    bathrooms: property.bathrooms,
    square_feet: property.square_feet,
    year_built: property.year_built,
    notes: property.notes,
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
          <h1 className="text-2xl font-semibold text-gray-900">Edit Property</h1>
          <p className="text-gray-600">{property.address}</p>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <PropertyForm
          propertyId={params.id}
          initialData={initialData}
          onSuccess={handleSuccess}
          onCancel={handleCancel}
        />
      </div>
    </div>
  );
}