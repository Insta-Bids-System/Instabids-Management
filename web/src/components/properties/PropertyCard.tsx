'use client';

import { Property } from '@/packages/shared/src/types/property';
import { Home, MapPin, Bed, Bath, Square } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface PropertyCardProps {
  property: Property;
  onClick?: () => void;
}

export default function PropertyCard({ property, onClick }: PropertyCardProps) {
  const router = useRouter();
  
  const formatPropertyType = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const handleCardClick = () => {
    if (onClick) {
      onClick();
    } else {
      router.push(`/properties/${property.id}`);
    }
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    router.push(`/properties/${property.id}/edit`);
  };

  const handleViewProjects = (e: React.MouseEvent) => {
    e.stopPropagation();
    router.push(`/projects?property=${property.id}`);
  };

  return (
    <div
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
      onClick={handleCardClick}
    >
      {/* Property Type Badge */}
      <div className="flex items-center justify-between mb-4">
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          {formatPropertyType(property.property_type)}
        </span>
        <Home className="w-5 h-5 text-gray-400" />
      </div>

      {/* Address */}
      <h3 className="font-semibold text-gray-900 mb-2">
        {property.address}
      </h3>
      
      <div className="flex items-center text-sm text-gray-500 mb-4">
        <MapPin className="w-4 h-4 mr-1" />
        {property.city}, {property.state} {property.zip_code}
      </div>

      {/* Property Details */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="flex items-center text-sm text-gray-600">
          <Bed className="w-4 h-4 mr-1" />
          {property.bedrooms} Beds
        </div>
        <div className="flex items-center text-sm text-gray-600">
          <Bath className="w-4 h-4 mr-1" />
          {property.bathrooms} Baths
        </div>
        <div className="flex items-center text-sm text-gray-600">
          <Square className="w-4 h-4 mr-1" />
          {property.square_feet.toLocaleString()} ft²
        </div>
      </div>

      {/* Year Built */}
      {property.year_built && (
        <div className="text-xs text-gray-500">
          Built in {property.year_built}
        </div>
      )}

      {/* Notes Preview */}
      {property.notes && (
        <p className="mt-3 text-sm text-gray-600 line-clamp-2">
          {property.notes}
        </p>
      )}

      {/* Action Buttons */}
      <div className="mt-4 flex gap-2">
        <button
          className="flex-1 px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 rounded hover:bg-blue-100 transition"
          onClick={handleEdit}
        >
          Edit
        </button>
        <button
          className="flex-1 px-3 py-1.5 text-sm font-medium text-gray-600 bg-gray-50 rounded hover:bg-gray-100 transition"
          onClick={handleViewProjects}
        >
          Projects
        </button>
      </div>
    </div>
  );
}