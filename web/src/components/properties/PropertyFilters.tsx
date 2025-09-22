'use client';

import { useState, useEffect } from 'react';
import { PropertyFilters as PropertyFiltersType, PropertyType } from '@/packages/shared/src/types/property';
import { Search, Filter, X } from 'lucide-react';

interface PropertyFiltersProps {
  onFiltersChange: (filters: PropertyFiltersType) => void;
}

const PROPERTY_TYPES: { value: PropertyType; label: string }[] = [
  { value: 'single_family', label: 'Single Family' },
  { value: 'condo', label: 'Condo' },
  { value: 'townhouse', label: 'Townhouse' },
  { value: 'multi_family', label: 'Multi Family' },
  { value: 'commercial', label: 'Commercial' },
  { value: 'land', label: 'Land' },
];

export default function PropertyFilters({ onFiltersChange }: PropertyFiltersProps) {
  const [search, setSearch] = useState('');
  const [propertyType, setPropertyType] = useState<PropertyType | ''>('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [minBedrooms, setMinBedrooms] = useState('');
  const [maxBedrooms, setMaxBedrooms] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Update filters when any value changes
  useEffect(() => {
    const filters: PropertyFiltersType = {};
    
    if (search.trim()) filters.search = search.trim();
    if (propertyType) filters.property_type = propertyType;
    if (city.trim()) filters.city = city.trim();
    if (state.trim()) filters.state = state.trim();
    if (minBedrooms) filters.min_bedrooms = parseInt(minBedrooms);
    if (maxBedrooms) filters.max_bedrooms = parseInt(maxBedrooms);

    onFiltersChange(filters);
  }, [search, propertyType, city, state, minBedrooms, maxBedrooms, onFiltersChange]);

  const clearFilters = () => {
    setSearch('');
    setPropertyType('');
    setCity('');
    setState('');
    setMinBedrooms('');
    setMaxBedrooms('');
    setShowAdvanced(false);
  };

  const hasActiveFilters = search || propertyType || city || state || minBedrooms || maxBedrooms;

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search properties by address..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Quick Filters */}
      <div className="flex flex-wrap gap-3 items-center">
        <select
          value={propertyType}
          onChange={(e) => setPropertyType(e.target.value as PropertyType | '')}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Types</option>
          {PROPERTY_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>

        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
        >
          <Filter className="w-4 h-4" />
          More Filters
        </button>

        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="flex items-center gap-2 px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition"
          >
            <X className="w-4 h-4" />
            Clear All
          </button>
        )}
      </div>

      {/* Advanced Filters */}
      {showAdvanced && (
        <div className="bg-gray-50 p-4 rounded-lg space-y-4">
          <h4 className="font-medium text-gray-900">Advanced Filters</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                City
              </label>
              <input
                type="text"
                placeholder="Enter city"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                State
              </label>
              <input
                type="text"
                placeholder="CA"
                value={state}
                onChange={(e) => setState(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                maxLength={2}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min Bedrooms
              </label>
              <select
                value={minBedrooms}
                onChange={(e) => setMinBedrooms(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Any</option>
                {[1, 2, 3, 4, 5, 6].map((num) => (
                  <option key={num} value={num}>{num}+</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Bedrooms
              </label>
              <select
                value={maxBedrooms}
                onChange={(e) => setMaxBedrooms(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Any</option>
                {[1, 2, 3, 4, 5, 6, 7, 8].map((num) => (
                  <option key={num} value={num}>{num}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}