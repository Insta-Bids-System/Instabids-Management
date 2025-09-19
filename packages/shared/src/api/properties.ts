import { Property, PropertyFormData, PropertyFilters } from '../types/property';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Shared API functions for both web and mobile
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

    const response = await fetch(`${API_URL}/api/properties?${params}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch properties');
    }

    return response.json();
  },

  // Get single property
  async getProperty(id: string): Promise<Property> {
    const response = await fetch(`${API_URL}/api/properties/${id}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch property');
    }

    return response.json();
  },

  // Create new property
  async createProperty(data: PropertyFormData): Promise<Property> {
    const response = await fetch(`${API_URL}/api/properties`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to create property');
    }

    return response.json();
  },

  // Update property
  async updateProperty(id: string, data: Partial<PropertyFormData>): Promise<Property> {
    const response = await fetch(`${API_URL}/api/properties/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to update property');
    }

    return response.json();
  },

  // Delete property
  async deleteProperty(id: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/properties/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to delete property');
    }
  },
};