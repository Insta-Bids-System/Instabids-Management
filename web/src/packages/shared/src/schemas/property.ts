import { z } from 'zod';

// Shared validation schemas for web and mobile
export const propertyTypeSchema = z.enum([
  'single_family',
  'condo',
  'townhouse',
  'multi_family',
  'commercial',
  'land'
]);

export const propertyFormSchema = z.object({
  address: z.string().min(5, 'Address must be at least 5 characters'),
  city: z.string().min(2, 'City is required'),
  state: z.string().length(2, 'State must be 2 characters'),
  zip_code: z.string().regex(/^\d{5}(-\d{4})?$/, 'Invalid zip code'),
  property_type: propertyTypeSchema,
  bedrooms: z.number().min(0).max(20),
  bathrooms: z.number().min(0).max(20),
  square_feet: z.number().min(100).max(100000),
  year_built: z.number().min(1800).max(new Date().getFullYear()).optional(),
  notes: z.string().max(500).optional()
});

export const propertyFilterSchema = z.object({
  property_type: propertyTypeSchema.optional(),
  city: z.string().optional(),
  state: z.string().length(2).optional(),
  min_bedrooms: z.number().min(0).optional(),
  max_bedrooms: z.number().max(20).optional(),
  search: z.string().optional()
});

export type PropertyFormData = z.infer<typeof propertyFormSchema>;
export type PropertyFilters = z.infer<typeof propertyFilterSchema>;