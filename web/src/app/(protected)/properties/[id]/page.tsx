'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Property } from '@/packages/shared/src/types/property';
import { propertiesApi } from '@/api/properties';
import { ArrowLeft, Edit, Trash2, MapPin, Home, Calendar, Loader2 } from 'lucide-react';

interface PropertyDetailPageProps {
  params: { id: string };
}

export default function PropertyDetailPage({ params }: PropertyDetailPageProps) {
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

  const handleEdit = () => {
    router.push(`/properties/${params.id}/edit`);
  };

  const handleDelete = async () => {
    if (!property) return;
    
    if (confirm('Are you sure you want to delete this property? This action cannot be undone.')) {
      try {
        await propertiesApi.deleteProperty(property.id);
        router.push('/properties');
      } catch (err) {
        alert('Failed to delete property. Please try again.');
        console.error(err);
      }
    }
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

  const formatPropertyType = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button
          onClick={() => router.back()}
          className="p-2 hover:bg-gray-100 rounded-lg transition"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-semibold text-gray-900">{property.address}</h1>
          <p className="text-gray-600 flex items-center gap-1">
            <MapPin className="w-4 h-4" />
            {property.city}, {property.state} {property.zip_code}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleEdit}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            <Edit className="w-4 h-4" />
            Edit
          </button>
          <button
            onClick={handleDelete}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
          >
            <Trash2 className="w-4 h-4" />
            Delete
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Property Overview */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Property Overview</h2>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <Home className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                <div className="text-sm text-gray-600">Type</div>
                <div className="font-semibold">{formatPropertyType(property.property_type)}</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600">Bedrooms</div>
                <div className="font-semibold text-lg">{property.bedrooms}</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600">Bathrooms</div>
                <div className="font-semibold text-lg">{property.bathrooms}</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600">Square Feet</div>
                <div className="font-semibold text-lg">{property.square_feet.toLocaleString()}</div>
              </div>
            </div>

            {property.year_built && (
              <div className="flex items-center gap-2 text-gray-600 mb-4">
                <Calendar className="w-4 h-4" />
                <span>Built in {property.year_built}</span>
              </div>
            )}

            {property.notes && (
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Notes</h3>
                <p className="text-gray-600 leading-relaxed">{property.notes}</p>
              </div>
            )}
          </div>

          {/* Location Details */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Location</h2>
            <div className="space-y-3">
              <div>
                <span className="text-sm font-medium text-gray-700">Full Address:</span>
                <div className="text-gray-900">
                  {property.address}<br />
                  {property.city}, {property.state} {property.zip_code}
                </div>
              </div>
              {property.coordinates && (
                <div>
                  <span className="text-sm font-medium text-gray-700">Coordinates:</span>
                  <div className="text-gray-900">
                    {property.coordinates.lat.toFixed(6)}, {property.coordinates.lng.toFixed(6)}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
                Create Project
              </button>
              <button className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition">
                View Projects
              </button>
              <button className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition">
                Add Photos
              </button>
            </div>
          </div>

          {/* Property Info */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Property Information</h3>
            <div className="space-y-3 text-sm">
              <div>
                <span className="text-gray-600">Property ID:</span>
                <div className="font-mono text-xs text-gray-500">{property.id}</div>
              </div>
              <div>
                <span className="text-gray-600">Created:</span>
                <div>{new Date(property.created_at).toLocaleDateString()}</div>
              </div>
              <div>
                <span className="text-gray-600">Last Updated:</span>
                <div>{new Date(property.updated_at).toLocaleDateString()}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}