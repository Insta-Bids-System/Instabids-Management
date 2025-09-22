// Shared property types for web and mobile
export interface Property {
  id: string;
  organization_id: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  property_type: PropertyType;
  bedrooms: number;
  bathrooms: number;
  square_feet: number;
  year_built?: number;
  notes?: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
  created_at: string;
  updated_at: string;
}

export type PropertyType = 
  | 'single_family'
  | 'condo'
  | 'townhouse'
  | 'multi_family'
  | 'commercial'
  | 'land';

export interface PropertyFormData {
  address: string;
  city: string;
  state: string;
  zip_code: string;
  property_type: PropertyType;
  bedrooms: number;
  bathrooms: number;
  square_feet: number;
  year_built?: number;
  notes?: string;
}

export interface PropertyFilters {
  property_type?: PropertyType;
  city?: string;
  state?: string;
  min_bedrooms?: number;
  max_bedrooms?: number;
  search?: string;
}