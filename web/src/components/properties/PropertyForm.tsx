'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { propertyFormSchema, PropertyFormData } from '@/packages/shared/src/schemas/property';
import { propertiesApi } from '@/api/properties';
import { useState } from 'react';
import { Loader2 } from 'lucide-react';

interface PropertyFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
  initialData?: Partial<PropertyFormData>;
  propertyId?: string;
}

export default function PropertyForm({ 
  onSuccess, 
  onCancel, 
  initialData,
  propertyId 
}: PropertyFormProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PropertyFormData>({
    resolver: zodResolver(propertyFormSchema),
    defaultValues: initialData,
  });

  const onSubmit = async (data: PropertyFormData) => {
    try {
      setLoading(true);
      setError(null);
      
      if (propertyId) {
        await propertiesApi.updateProperty(propertyId, data);
      } else {
        await propertiesApi.createProperty(data);
      }
      
      onSuccess?.();
    } catch (err) {
      setError('Failed to save property. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Address Section */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900">Property Address</h3>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Street Address
          </label>
          <input
            {...register('address')}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="123 Main Street"
          />
          {errors.address && (
            <p className="mt-1 text-sm text-red-600">{errors.address.message}</p>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              City
            </label>
            <input
              {...register('city')}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="San Francisco"
            />
            {errors.city && (
              <p className="mt-1 text-sm text-red-600">{errors.city.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              State
            </label>
            <input
              {...register('state')}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="CA"
              maxLength={2}
            />
            {errors.state && (
              <p className="mt-1 text-sm text-red-600">{errors.state.message}</p>
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Zip Code
          </label>
          <input
            {...register('zip_code')}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="94102"
          />
          {errors.zip_code && (
            <p className="mt-1 text-sm text-red-600">{errors.zip_code.message}</p>
          )}
        </div>
      </div>

      {/* Property Details */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900">Property Details</h3>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Property Type
          </label>
          <select
            {...register('property_type')}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select type</option>
            <option value="single_family">Single Family</option>
            <option value="condo">Condo</option>
            <option value="townhouse">Townhouse</option>
            <option value="multi_family">Multi Family</option>
            <option value="commercial">Commercial</option>
            <option value="land">Land</option>
          </select>
          {errors.property_type && (
            <p className="mt-1 text-sm text-red-600">{errors.property_type.message}</p>
          )}
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Bedrooms
            </label>
            <input
              type="number"
              {...register('bedrooms', { valueAsNumber: true })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="3"
              min="0"
            />
            {errors.bedrooms && (
              <p className="mt-1 text-sm text-red-600">{errors.bedrooms.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Bathrooms
            </label>
            <input
              type="number"
              step="0.5"
              {...register('bathrooms', { valueAsNumber: true })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="2"
              min="0"
            />
            {errors.bathrooms && (
              <p className="mt-1 text-sm text-red-600">{errors.bathrooms.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Square Feet
            </label>
            <input
              type="number"
              {...register('square_feet', { valueAsNumber: true })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="1500"
              min="100"
            />
            {errors.square_feet && (
              <p className="mt-1 text-sm text-red-600">{errors.square_feet.message}</p>
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Year Built (Optional)
          </label>
          <input
            type="number"
            {...register('year_built', { valueAsNumber: true })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="1990"
            min="1800"
            max={new Date().getFullYear()}
          />
          {errors.year_built && (
            <p className="mt-1 text-sm text-red-600">{errors.year_built.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notes (Optional)
          </label>
          <textarea
            {...register('notes')}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Additional property notes..."
          />
          {errors.notes && (
            <p className="mt-1 text-sm text-red-600">{errors.notes.message}</p>
          )}
        </div>
      </div>

      {/* Form Actions */}
      <div className="flex gap-4">
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
          disabled={loading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          disabled={loading}
        >
          {loading && <Loader2 className="w-4 h-4 animate-spin" />}
          {propertyId ? 'Update' : 'Create'} Property
        </button>
      </div>
    </form>
  );
}