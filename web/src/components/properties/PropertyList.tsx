'use client';

import { useState, useEffect } from 'react';
import { Property, PropertyFilters } from '@/packages/shared/src/types/property';
import { propertiesApi } from '@/api/properties';
import PropertyCard from './PropertyCard';
import PropertyFilters from './PropertyFilters';
import { Plus, Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function PropertyList() {
  const router = useRouter();
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<PropertyFilters>({});

  useEffect(() => {
    loadProperties();
  }, [filters]);

  const loadProperties = async () => {
    try {
      setLoading(true);
      const data = await propertiesApi.getProperties(filters);
      setProperties(data);
      setError(null);
    } catch (err) {
      setError('Failed to load properties');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Properties</h1>
        <button
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          onClick={() => router.push('/properties/new')}
        >
          <Plus className="w-5 h-5" />
          Add Property
        </button>
      </div>

      {/* Filters */}
      <PropertyFilters onFiltersChange={setFilters} />

      {/* Properties Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {properties.length === 0 ? (
          <div className="col-span-full text-center py-12 text-gray-500">
            No properties found. Add your first property to get started.
          </div>
        ) : (
          properties.map((property) => (
            <PropertyCard key={property.id} property={property} />
          ))
        )}
      </div>
    </div>
  );
}