# Property Management Feature Specification

## Overview
Enable property managers to create, organize, and manage their property portfolios with comprehensive details for maintenance tracking.

## User Stories

### As a Property Manager
- I want to add properties to my portfolio so I can track all locations
- I want to organize properties by type and location for better management
- I want to assign properties to specific team members for responsibility tracking
- I want to view property history and maintenance schedules at a glance
- I want to bulk import properties from spreadsheets to save time

### As an Admin
- I want to see all properties across the organization for oversight
- I want to track property performance metrics for reporting
- I want to ensure properties have complete information for accurate quotes

## Functional Requirements

### Property CRUD Operations
1. **Create Property**
   - Add single property with full details
   - Required: address, type, manager assignment
   - Optional: units, square footage, year built, amenities
   - Photo upload for property documentation
   - Automatic geocoding for mapping

2. **View Properties**
   - List view with filtering and search
   - Card view with property photos
   - Map view showing all locations
   - Property detail page with full information

3. **Update Property**
   - Edit all property details
   - Change manager assignments
   - Update photos and documents
   - Add/remove amenities and features

4. **Delete Property**
   - Soft delete with recovery option
   - Archive old properties
   - Bulk delete operations
   - Cascade handling for related projects

### Property Organization
1. **Property Types**
   - Residential (single-family, multi-family, apartment)
   - Commercial (office, retail, industrial)
   - Mixed-use properties
   - Custom categories

2. **Property Groups**
   - Create portfolios/groups
   - Assign properties to multiple groups
   - Group-level permissions
   - Bulk operations on groups

3. **Property Search**
   - Search by address, name, or ID
   - Filter by type, manager, status
   - Geographic radius search
   - Advanced filters (year built, size, etc.)

### Data Management
1. **Import/Export**
   - CSV import with mapping
   - Excel template download
   - Bulk update via spreadsheet
   - Export filtered lists

2. **Property Templates**
   - Save property as template
   - Apply template to new properties
   - Share templates across organization

## Technical Requirements

### Database Schema
```sql
-- Properties table (extends existing)
properties:
  - id: uuid
  - organization_id: uuid
  - name: string
  - address: string
  - city: string
  - state: string
  - zip: string
  - country: string
  - property_type: enum
  - status: enum (active, inactive, archived)
  - manager_id: uuid (ref: user_profiles)
  - details: jsonb
    - square_footage: number
    - year_built: number
    - units: number
    - floors: number
    - parking_spaces: number
  - amenities: string[]
  - coordinates: point
  - photos: jsonb[]
  - created_at: timestamp
  - updated_at: timestamp
  - deleted_at: timestamp (soft delete)

-- Property groups
property_groups:
  - id: uuid
  - organization_id: uuid
  - name: string
  - description: text
  - created_by: uuid
  - created_at: timestamp

-- Property group members
property_group_members:
  - property_id: uuid
  - group_id: uuid
  - added_at: timestamp
```

### API Endpoints
```yaml
Properties:
  POST   /api/properties          # Create property
  GET    /api/properties          # List properties
  GET    /api/properties/:id      # Get property details
  PUT    /api/properties/:id      # Update property
  DELETE /api/properties/:id      # Delete property
  POST   /api/properties/bulk     # Bulk operations
  POST   /api/properties/import   # Import from file
  GET    /api/properties/export   # Export to file

Groups:
  POST   /api/property-groups     # Create group
  GET    /api/property-groups     # List groups
  PUT    /api/property-groups/:id # Update group
  DELETE /api/property-groups/:id # Delete group
  POST   /api/property-groups/:id/members # Add properties
  DELETE /api/property-groups/:id/members # Remove properties
```

### Frontend Components
```typescript
// Core Components
<PropertyList />       // Main list/grid view
<PropertyCard />       // Individual property card
<PropertyDetail />     // Full property page
<PropertyForm />       // Create/Edit form
<PropertyMap />        // Map visualization
<PropertyImport />     // Import wizard

// Supporting Components
<PropertyFilter />     // Advanced filtering
<PropertySearch />     // Search bar
<PropertyBulkActions /> // Bulk operations menu
<PropertyTypeSelect /> // Type selector
<PropertyGroupSelect /> // Group assignment
```

## User Interface

### Property List Page
```
[+ Add Property] [Import] [Export]

[Search...] [Filter: All Types v] [Group: All v]

[List View] [Card View] [Map View]

+------------------------+
| Property Name          |
| 123 Main St            |
| Type: Commercial       |
| Manager: John Doe      |
| [Edit] [Archive]       |
+------------------------+
```

### Property Form
```
Add New Property

Basic Information
  Name*: [_______________]
  Address*: [_______________]
  City*: [_______] State: [__] ZIP: [______]
  
Property Details
  Type*: [Select Type v]
  Manager*: [Select Manager v]
  Square Footage: [_______]
  Year Built: [____]
  Units: [__]
  
Amenities
  [ ] Parking
  [ ] Elevator
  [ ] Security System
  [ ] HVAC
  [+ Add Custom]
  
Photos
  [Drop files or click to upload]
  
[Cancel] [Save Property]
```

## Business Logic

### Validation Rules
1. Address must be unique within organization
2. Manager must be active user in organization
3. Year built cannot be future date
4. At least one photo recommended
5. Coordinates auto-generated from address

### Permissions
- **Admin**: Full CRUD on all properties
- **Manager**: CRUD on assigned properties
- **Viewer**: Read-only access

### Automation
1. Geocode addresses on save
2. Generate property ID/code
3. Send notification on manager change
4. Update audit log on changes

## Success Criteria
- [ ] Property managers can add 10 properties in < 5 minutes
- [ ] Search returns results in < 500ms
- [ ] Map loads 100 properties smoothly
- [ ] Import handles 1000 properties without timeout
- [ ] Mobile responsive with touch-friendly interface

## Dependencies
- Google Maps API for geocoding
- AWS S3 for photo storage
- Existing user authentication system
- Organization management system

## Security Considerations
- RLS policies enforce organization boundaries
- File upload validation (type, size)
- SQL injection prevention
- XSS protection on property names/descriptions

## Future Enhancements
- QR codes for property identification
- Virtual tour integration
- Maintenance schedule templates
- Cost tracking per property
- Tenant portal access