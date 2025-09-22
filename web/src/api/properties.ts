import { Property, PropertyFormData, PropertyFilters } from '@/packages/shared/src/types/property';
import { authenticatedFetch } from '@/utils/api';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Web-specific API functions using web project dependencies
export const propertiesApi = {
  // Get all properties with optional filters
  async getProperties(filters?: PropertyFilters): Promise<Property[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, String(value));
        }
      });
    }

    const response = await authenticatedFetch(`${API_URL}/api/properties?${params}`);

    if (!response.ok) {
      throw new Error('Failed to fetch properties');
    }

    return response.json();
  },

  // Get single property
  async getProperty(id: string): Promise<Property> {
    const response = await authenticatedFetch(`${API_URL}/api/properties/${id}`);

    if (!response.ok) {
      throw new Error('Failed to fetch property');
    }

    return response.json();
  },

  // Create new property
  async createProperty(data: PropertyFormData): Promise<Property> {
    const response = await authenticatedFetch(`${API_URL}/api/properties`, {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to create property');
    }

    return response.json();
  },

  // Update property
  async updateProperty(id: string, data: Partial<PropertyFormData>): Promise<Property> {
    const response = await authenticatedFetch(`${API_URL}/api/properties/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to update property');
    }

    return response.json();
  },

  // Delete property
  async deleteProperty(id: string): Promise<void> {
    const response = await authenticatedFetch(`${API_URL}/api/properties/${id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to delete property');
    }
  },
};