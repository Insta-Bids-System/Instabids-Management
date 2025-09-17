-- Migration 003: Property Management Enhancement
-- Adds complete property management functionality

-- Create property type enum
CREATE TYPE property_type AS ENUM (
  'single_family',
  'multi_family',
  'apartment',
  'condo',
  'townhouse',
  'commercial_office',
  'commercial_retail',
  'commercial_industrial',
  'mixed_use',
  'other'
);

-- Create property status enum
CREATE TYPE property_status AS ENUM (
  'active',
  'inactive',
  'archived'
);

-- Extend properties table with full schema
ALTER TABLE properties
ADD COLUMN IF NOT EXISTS property_type property_type DEFAULT 'other',
ADD COLUMN IF NOT EXISTS status property_status DEFAULT 'active',
ADD COLUMN IF NOT EXISTS manager_id UUID REFERENCES user_profiles(id),
ADD COLUMN IF NOT EXISTS city VARCHAR(100),
ADD COLUMN IF NOT EXISTS state VARCHAR(50),
ADD COLUMN IF NOT EXISTS zip VARCHAR(20),
ADD COLUMN IF NOT EXISTS country VARCHAR(100) DEFAULT 'USA',
ADD COLUMN IF NOT EXISTS details JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS amenities TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS coordinates POINT,
ADD COLUMN IF NOT EXISTS photos JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;

-- Create property groups table
CREATE TABLE IF NOT EXISTS property_groups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_by UUID NOT NULL REFERENCES user_profiles(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  CONSTRAINT unique_group_name_per_org UNIQUE (organization_id, name)
);

-- Create property group members junction table
CREATE TABLE IF NOT EXISTS property_group_members (
  property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  group_id UUID NOT NULL REFERENCES property_groups(id) ON DELETE CASCADE,
  added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  added_by UUID REFERENCES user_profiles(id),
  
  PRIMARY KEY (property_id, group_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_properties_organization_status 
  ON properties(organization_id, status) 
  WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_properties_manager 
  ON properties(manager_id) 
  WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_properties_type 
  ON properties(property_type);

CREATE INDEX IF NOT EXISTS idx_properties_coordinates 
  ON properties USING GIST(coordinates) 
  WHERE coordinates IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_property_groups_organization 
  ON property_groups(organization_id);

CREATE INDEX IF NOT EXISTS idx_property_group_members_group 
  ON property_group_members(group_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add updated_at triggers
CREATE TRIGGER update_properties_updated_at
  BEFORE UPDATE ON properties
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_property_groups_updated_at
  BEFORE UPDATE ON property_groups
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- RLS Policies for properties
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view properties in their organization
CREATE POLICY "Users can view organization properties"
  ON properties FOR SELECT
  USING (
    organization_id IN (
      SELECT organization_id FROM user_profiles
      WHERE id = auth.uid()
    )
    AND deleted_at IS NULL
  );

-- Policy: Admins and managers can create properties
CREATE POLICY "Admins and managers can create properties"
  ON properties FOR INSERT
  WITH CHECK (
    organization_id IN (
      SELECT organization_id FROM user_profiles
      WHERE id = auth.uid()
      AND role IN ('admin', 'manager')
    )
  );

-- Policy: Admins can update any property, managers can update assigned properties
CREATE POLICY "Update property permissions"
  ON properties FOR UPDATE
  USING (
    organization_id IN (
      SELECT organization_id FROM user_profiles
      WHERE id = auth.uid()
    )
    AND (
      EXISTS (
        SELECT 1 FROM user_profiles
        WHERE id = auth.uid()
        AND role = 'admin'
      )
      OR manager_id = auth.uid()
    )
  );

-- Policy: Only admins can delete properties
CREATE POLICY "Only admins can delete properties"
  ON properties FOR DELETE
  USING (
    organization_id IN (
      SELECT organization_id FROM user_profiles
      WHERE id = auth.uid()
      AND role = 'admin'
    )
  );

-- RLS Policies for property_groups
ALTER TABLE property_groups ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view groups in their organization
CREATE POLICY "Users can view organization groups"
  ON property_groups FOR SELECT
  USING (
    organization_id IN (
      SELECT organization_id FROM user_profiles
      WHERE id = auth.uid()
    )
  );

-- Policy: Admins and managers can manage groups
CREATE POLICY "Admins and managers can create groups"
  ON property_groups FOR INSERT
  WITH CHECK (
    organization_id IN (
      SELECT organization_id FROM user_profiles
      WHERE id = auth.uid()
      AND role IN ('admin', 'manager')
    )
  );

CREATE POLICY "Admins and managers can update groups"
  ON property_groups FOR UPDATE
  USING (
    organization_id IN (
      SELECT organization_id FROM user_profiles
      WHERE id = auth.uid()
      AND role IN ('admin', 'manager')
    )
  );

CREATE POLICY "Admins can delete groups"
  ON property_groups FOR DELETE
  USING (
    organization_id IN (
      SELECT organization_id FROM user_profiles
      WHERE id = auth.uid()
      AND role = 'admin'
    )
  );

-- RLS Policies for property_group_members
ALTER TABLE property_group_members ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view group members if they can view the group
CREATE POLICY "Users can view group members"
  ON property_group_members FOR SELECT
  USING (
    group_id IN (
      SELECT id FROM property_groups
      WHERE organization_id IN (
        SELECT organization_id FROM user_profiles
        WHERE id = auth.uid()
      )
    )
  );

-- Policy: Admins and managers can manage group members
CREATE POLICY "Admins and managers can manage group members"
  ON property_group_members FOR ALL
  USING (
    group_id IN (
      SELECT id FROM property_groups
      WHERE organization_id IN (
        SELECT organization_id FROM user_profiles
        WHERE id = auth.uid()
        AND role IN ('admin', 'manager')
      )
    )
  );

-- Create audit log for property changes
CREATE TABLE IF NOT EXISTS property_audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  action VARCHAR(50) NOT NULL,
  changes JSONB,
  performed_by UUID NOT NULL REFERENCES user_profiles(id),
  performed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  INDEX idx_property_audit_property (property_id),
  INDEX idx_property_audit_performed_at (performed_at DESC)
);

-- Sample data for testing (commented out for production)
/*
-- Insert sample property types
INSERT INTO properties (
  organization_id,
  name,
  address,
  city,
  state,
  zip,
  property_type,
  status,
  details,
  amenities
)
SELECT 
  o.id,
  'Sample Property ' || generate_series,
  generate_series || ' Main Street',
  'San Francisco',
  'CA',
  '94105',
  (ARRAY['single_family', 'multi_family', 'apartment', 'commercial_office'])[1 + generate_series % 4]::property_type,
  'active',
  jsonb_build_object(
    'square_footage', 1000 + (generate_series * 100),
    'year_built', 1990 + generate_series,
    'units', generate_series
  ),
  ARRAY['parking', 'elevator', 'security']
FROM organizations o
CROSS JOIN generate_series(1, 5)
WHERE o.name = 'Default Organization';
*/