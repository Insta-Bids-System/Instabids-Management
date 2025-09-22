# InstaBids Management - Complete API Examples

**Every API Pattern Your Agents Need**

## 🔐 Authentication Setup

### Required Headers for All Requests
```javascript
const headers = {
  'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxtYnB2a2ZjZmhkZmFpaGlnZmR1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzY1MTUzNjAsImV4cCI6MjA1MjA5MTM2MH0.gkkLdn-7wQWzY_o0oa9YzYX8QjHShLdJObqJfb3Tnmg',
  'Authorization': 'Bearer YOUR_JWT_TOKEN',
  'Content-Type': 'application/json',
  'Prefer': 'return=representation' // Get full object back after operations
}
```

### Base URLs
```javascript
const BASE_URL = 'https://lmbpvkfcfhdfaihigfdu.supabase.co'
const REST_API = `${BASE_URL}/rest/v1`
const AUTH_API = `${BASE_URL}/auth/v1`
const STORAGE_API = `${BASE_URL}/storage/v1`
```

---

## 🏢 Organizations API

### Get User's Organization
```javascript
GET ${REST_API}/organizations?select=*

// RLS automatically filters to user's organization
// Returns organization details, settings, billing info
```

### Update Organization (Property Managers Only)  
```javascript
PATCH ${REST_API}/organizations?id=eq.{org_id}
{
  "name": "Updated Org Name",
  "settings": {
    "timezone": "America/New_York",
    "notifications": true
  },
  "billing_info": {
    "plan": "premium"
  }
}
```

---

## 👤 User Profiles API

### Get Current User Profile
```javascript
GET ${REST_API}/user_profiles?id=eq.{user_id}&select=*

// Returns current user's profile with organization details
```

### Update User Profile
```javascript
PATCH ${REST_API}/user_profiles?id=eq.{user_id}
{
  "full_name": "John Smith",
  "phone": "+1-555-123-4567",
  "preferences": {
    "email_notifications": true,
    "timezone": "America/New_York"
  },
  "profile_data": {
    "title": "Property Manager",
    "department": "Operations"
  }
}
```

### Create New User Profile
```javascript
POST ${REST_API}/user_profiles
{
  "id": "{auth_user_id}",
  "email": "user@example.com",
  "full_name": "New User",
  "user_type": "property_manager",
  "organization_id": "{org_id}",
  "is_active": true
}
```

---

## 🏠 Properties API

### Get All Organization Properties
```javascript
GET ${REST_API}/properties?is_deleted=eq.false&order=created_at.desc&select=*

// RLS filters to organization properties only
// Returns all active properties with full details
```

### Get Properties with Filtering
```javascript
// Filter by property type
GET ${REST_API}/properties?property_type=eq.single_family&is_deleted=eq.false

// Filter by city  
GET ${REST_API}/properties?city=eq.Boston&is_deleted=eq.false

// Filter by manager
GET ${REST_API}/properties?manager_id=eq.{user_id}&is_deleted=eq.false

// Search by name or address
GET ${REST_API}/properties?or=(name.ilike.*search*,address.ilike.*search*)&is_deleted=eq.false
```

### Create New Property
```javascript
POST ${REST_API}/properties
{
  "organization_id": "{org_id}",
  "name": "Sunrise Apartments",
  "address": "123 Main Street",
  "city": "Boston",
  "state": "Massachusetts", 
  "zip_code": "02101",
  "country": "United States",
  "property_type": "multi_family",
  "property_status": "active",
  "units": 24,
  "bedrooms": 2,
  "bathrooms": 1.5,
  "square_feet": 1200,
  "year_built": 1985,
  "manager_id": "{user_id}",
  "property_data": {
    "parking_spaces": 30,
    "amenities": ["pool", "gym", "laundry"]
  },
  "notes": "Recently renovated common areas"
}
```

### Update Property
```javascript
PATCH ${REST_API}/properties?id=eq.{property_id}
{
  "name": "Updated Property Name",
  "property_status": "inactive",
  "manager_id": "{new_manager_id}",
  "property_data": {
    "last_inspection": "2025-01-15",
    "condition": "good"
  }
}
```

### Get Property with Projects and Media
```javascript
GET ${REST_API}/properties?id=eq.{property_id}&select=*,projects(*,project_media(*))

// Returns property with all related projects and their media
```

---

## 📋 Projects API

### Get Organization Projects
```javascript
GET ${REST_API}/projects?select=*,properties(name,address,city),user_profiles(full_name)&order=urgency.desc,created_at.desc

// Returns projects with property and creator details
// Ordered by urgency then creation date
```

### Get Projects by Status
```javascript
// Active projects
GET ${REST_API}/projects?status=in.(open_for_bids,in_progress)&select=*,properties(name,address)

// Completed projects
GET ${REST_API}/projects?status=eq.completed&select=*,properties(name,address)

// Emergency projects
GET ${REST_API}/projects?urgency=eq.emergency&select=*,properties(name,address)
```

### Get Projects for Specific Property
```javascript
GET ${REST_API}/projects?property_id=eq.{property_id}&order=created_at.desc&select=*,quotes(count)

// Returns all projects for property with quote counts
```

### Create New Project
```javascript
POST ${REST_API}/projects
{
  "property_id": "{property_id}",
  "title": "Fix Leaking Faucet in Unit 2A",
  "description": "Kitchen faucet in unit 2A has been leaking for 3 days. Tenant reports water damage risk.",
  "category": "plumbing",
  "urgency": "urgent",
  "status": "draft",
  "budget_min": 150.00,
  "budget_max": 500.00,
  "area": "Kitchen",
  "access_info": "Tenant available weekdays 9-5",
  "requirements": {
    "insurance_required": true,
    "background_check": true,
    "licensed_plumber": true
  },
  "created_by": "{user_id}"
}
```

### Update Project Status
```javascript
PATCH ${REST_API}/projects?id=eq.{project_id}
{
  "status": "open_for_bids",
  "timeline": "P3D", // 3 days in PostgreSQL interval format
  "requirements": {
    "start_date": "2025-01-20",
    "completion_deadline": "2025-01-23"
  }
}
```

### Get Project with All Related Data
```javascript
GET ${REST_API}/projects?id=eq.{project_id}&select=*,properties(name,address,city),project_media(*),quotes(*,contractors(business_name,rating_average)),smartscope_analyses(*),invitations(*,contractors(business_name))

// Returns complete project details with:
// - Property information
// - All media/photos
// - All quotes with contractor info
// - AI analysis results
// - All invitations sent
```

---

## 🔧 Contractors API

### Get All Verified Contractors
```javascript
GET ${REST_API}/contractors?verification_status=eq.verified&is_active=eq.true&order=rating_average.desc&select=*

// Returns all verified, active contractors ordered by rating
```

### Search Contractors by Specialty
```javascript
GET ${REST_API}/contractors?specialties=cs.{plumbing}&verification_status=eq.verified&select=*,contractor_credentials(*)

// Find contractors with plumbing specialty
// cs. = contains (array contains value)
```

### Search Contractors by Service Area
```javascript
GET ${REST_API}/contractors?service_areas=cs.{02101}&verification_status=eq.verified&select=*,contractor_availability(*)

// Find contractors serving ZIP code 02101
```

### Get Contractor with Full Profile
```javascript
GET ${REST_API}/contractors?id=eq.{contractor_id}&select=*,contractor_credentials(*),contractor_availability(*),contractor_portfolio(*),quotes(count)

// Returns contractor with:
// - All credentials and certifications
// - Service areas and availability  
// - Portfolio projects
// - Total quote count
```

### Create Contractor Profile
```javascript
POST ${REST_API}/contractors
{
  "user_id": "{user_id}",
  "business_name": "Smith Plumbing LLC",
  "contact_name": "John Smith",
  "email": "john@smithplumbing.com",
  "phone": "+1-555-123-4567",
  "business_type": "llc",
  "specialties": ["plumbing", "hvac"],
  "service_areas": ["02101", "02102", "02103"],
  "business_address": {
    "street": "456 Trade St",
    "city": "Boston",
    "state": "MA",
    "zip": "02101"
  },
  "verification_status": "pending_review",
  "profile_data": {
    "years_experience": 15,
    "employees": 5,
    "insurance_amount": 1000000
  }
}
```

---

## 💰 Quotes API

### Get Quotes for Project
```javascript
GET ${REST_API}/quotes?project_id=eq.{project_id}&order=total_amount.asc&select=*,contractors(business_name,rating_average),quote_line_items(*)

// Returns all quotes for project with:
// - Contractor details
// - Line item breakdowns
// - Ordered by price (lowest first)
```

### Get Contractor's Quotes
```javascript
GET ${REST_API}/quotes?contractor_id=eq.{contractor_id}&order=created_at.desc&select=*,projects(title,property_id,properties(name,address))

// Returns contractor's quotes with project details
```

### Create Quote
```javascript
POST ${REST_API}/quotes
{
  "project_id": "{project_id}",
  "contractor_id": "{contractor_id}",
  "quote_number": "Q-2025-001",
  "total_amount": 850.00,
  "labor_cost": 500.00,
  "material_cost": 300.00,
  "additional_costs": 50.00,
  "timeline_days": 2,
  "warranty_period": 365,
  "notes": "Includes replacement of main shut-off valve. 1-year warranty on all parts and labor.",
  "status": "received",
  "submission_method": "web_form",
  "submitted_at": "2025-01-17T10:30:00Z",
  "expires_at": "2025-02-01T23:59:59Z"
}
```

### Create Quote with Line Items
```javascript
// First create the quote
POST ${REST_API}/quotes
{
  "project_id": "{project_id}",
  "contractor_id": "{contractor_id}",
  "quote_number": "Q-2025-002",
  "total_amount": 1250.00,
  "status": "received"
}

// Then add line items
POST ${REST_API}/quote_line_items
[
  {
    "quote_id": "{quote_id}",
    "description": "Kitchen faucet replacement - high-end model",
    "quantity": 1.0,
    "unit_price": 350.00,
    "total_price": 350.00,
    "category": "materials",
    "line_order": 1
  },
  {
    "quote_id": "{quote_id}",
    "description": "Labor - faucet installation and testing",
    "quantity": 4.0,
    "unit_price": 125.00,
    "total_price": 500.00,
    "category": "labor",
    "line_order": 2
  },
  {
    "quote_id": "{quote_id}",
    "description": "Shut-off valve replacement",
    "quantity": 1.0,
    "unit_price": 75.00,
    "total_price": 75.00,
    "category": "materials",
    "line_order": 3
  }
]
```

### Update Quote Status
```javascript
PATCH ${REST_API}/quotes?id=eq.{quote_id}
{
  "status": "standardized",
  "metadata": {
    "processed_by": "{user_id}",
    "processing_notes": "Quote reviewed and standardized"
  }
}
```

---

## 🏆 Awards API

### Award Project to Contractor
```javascript
POST ${REST_API}/awards
{
  "project_id": "{project_id}",
  "contractor_id": "{contractor_id}",
  "quote_id": "{quote_id}",
  "awarded_by": "{user_id}",
  "award_amount": 850.00,
  "award_notes": "Selected for competitive pricing and excellent references",
  "start_date": "2025-01-20",
  "expected_completion_date": "2025-01-22"
}

// Also update project status
PATCH ${REST_API}/projects?id=eq.{project_id}
{
  "status": "awarded"
}
```

### Get Organization Awards
```javascript
GET ${REST_API}/awards?select=*,projects(title,properties(name,address)),contractors(business_name),quotes(total_amount)&order=created_at.desc

// Returns all awards with project, property, and contractor details
```

### Complete Project
```javascript
PATCH ${REST_API}/awards?id=eq.{award_id}
{
  "actual_completion_date": "2025-01-22"
}

PATCH ${REST_API}/projects?id=eq.{project_id}
{
  "status": "completed",
  "completion_notes": "Work completed satisfactorily. All issues resolved."
}
```

---

## 📨 Invitations API

### Send Invitations to Contractors
```javascript
POST ${REST_API}/invitations
[
  {
    "project_id": "{project_id}",
    "contractor_id": "{contractor_id_1}",
    "invited_by": "{user_id}",
    "message": "We have a plumbing project that matches your expertise. Please review and submit a quote if interested.",
    "expires_at": "2025-02-01T23:59:59Z"
  },
  {
    "project_id": "{project_id}",
    "contractor_id": "{contractor_id_2}",
    "invited_by": "{user_id}",
    "message": "Urgent plumbing repair needed. Please respond quickly if available.",
    "expires_at": "2025-02-01T23:59:59Z"
  }
]
```

### Get Project Invitations
```javascript
GET ${REST_API}/invitations?project_id=eq.{project_id}&select=*,contractors(business_name,email,phone)&order=invited_at.desc

// Returns all invitations for project with contractor contact info
```

### Update Invitation Status (Contractor Response)
```javascript
PATCH ${REST_API}/invitations?project_id=eq.{project_id}&contractor_id=eq.{contractor_id}
{
  "status": "accepted",
  "responded_at": "2025-01-17T14:30:00Z"
}
```

---

## 🤖 SmartScope AI Analysis API

### Get AI Analysis for Project
```javascript
GET ${REST_API}/smartscope_analyses?project_id=eq.{project_id}&order=created_at.desc&select=*

// Returns AI analysis results for project photos
```

### Create AI Analysis
```javascript
POST ${REST_API}/smartscope_analyses
{
  "project_id": "{project_id}",
  "photo_urls": [
    "https://storage.supabase.co/photos/leak1.jpg",
    "https://storage.supabase.co/photos/leak2.jpg"
  ],
  "primary_issue": "Kitchen faucet leaking at base connection",
  "severity": "medium",
  "category": "plumbing",
  "estimated_hours": 2.5,
  "safety_notes": "Water damage risk if not addressed within 48 hours",
  "confidence_score": 0.92,
  "openai_response_raw": {
    "model": "gpt-4-vision-preview",
    "response": "...",
    "usage": {}
  },
  "additional_observations": [
    "Mineral buildup visible on faucet",
    "Water staining on cabinet below",
    "Appears to be original 1980s fixture"
  ]
}
```

---

## 📷 Project Media API

### Upload Project Media
```javascript
POST ${REST_API}/project_media
{
  "project_id": "{project_id}",
  "file_name": "kitchen_leak_photo1.jpg",
  "file_path": "/project_photos/2025/01/{project_id}/kitchen_leak_photo1.jpg",
  "file_type": "jpg",
  "file_size": 2458392,
  "media_type": "photo",
  "description": "Kitchen faucet leak - main view",
  "uploaded_by": "{user_id}"
}
```

### Get Project Media
```javascript
GET ${REST_API}/project_media?project_id=eq.{project_id}&order=uploaded_at.desc&select=*

// Returns all media for project ordered by upload date
```

---

## 🔍 Advanced Filtering and Search

### Full-Text Search Across Projects
```javascript
GET ${REST_API}/projects?or=(title.ilike.*leak*,description.ilike.*leak*)&select=*,properties(name,address)

// Search for "leak" in project titles or descriptions
```

### Complex Filtering with Multiple Conditions
```javascript
GET ${REST_API}/projects?urgency=in.(emergency,urgent)&status=eq.open_for_bids&created_at=gte.2025-01-01&select=*,properties(name,city),quotes(count)

// Find urgent projects open for bids created this year
// Include property details and quote counts
```

### Aggregation Queries
```javascript
// Count projects by status
GET ${REST_API}/projects?select=status,count&group=status

// Count projects by category
GET ${REST_API}/projects?select=category,count&group=category

// Average quote amounts by category
GET ${REST_API}/quotes?select=projects(category),total_amount.avg()&group=projects.category
```

---

## 📊 Common Business Logic Patterns

### Dashboard Data (Properties Manager)
```javascript
// Get summary counts
GET ${REST_API}/properties?select=count&is_deleted=eq.false
GET ${REST_API}/projects?select=count&status=eq.open_for_bids  
GET ${REST_API}/projects?select=count&status=eq.in_progress
GET ${REST_API}/projects?select=count&urgency=eq.emergency

// Get recent activity
GET ${REST_API}/projects?order=created_at.desc&limit=10&select=*,properties(name)
GET ${REST_API}/quotes?order=submitted_at.desc&limit=10&select=*,projects(title),contractors(business_name)
```

### Contractor Dashboard Data
```javascript
// Get contractor's active quotes
GET ${REST_API}/quotes?contractor_id=eq.{contractor_id}&status=in.(received,processing)&select=*,projects(title,urgency,properties(name,city))

// Get contractor's completed projects  
GET ${REST_API}/awards?contractor_id=eq.{contractor_id}&select=*,projects(title,properties(name)),quotes(total_amount)&order=created_at.desc

// Get pending invitations
GET ${REST_API}/invitations?contractor_id=eq.{contractor_id}&status=eq.sent&select=*,projects(title,category,urgency,properties(name,city))
```

### Project Workflow Status
```javascript
// Check if project is ready for quotes
GET ${REST_API}/projects?id=eq.{project_id}&status=eq.open_for_bids&select=*,invitations(count)

// Get quote comparison data
GET ${REST_API}/quotes?project_id=eq.{project_id}&status=eq.standardized&order=total_amount.asc&select=*,contractors(business_name,rating_average),quote_line_items(*)
```

---

## 🚨 Error Handling

### Common HTTP Status Codes
```javascript
// 200 - Success
// 201 - Created  
// 400 - Bad Request (invalid data)
// 401 - Unauthorized (no/invalid token)
// 403 - Forbidden (RLS policy denied)
// 404 - Not Found
// 409 - Conflict (unique constraint violation)
// 422 - Unprocessable Entity (validation failed)
```

### Error Response Format
```javascript
{
  "error": {
    "message": "Error description",
    "details": "Additional error details",
    "hint": "Suggestion for fixing",
    "code": "PGRST116" // PostgREST error code
  }
}
```

### RLS Policy Violations
```javascript
// When RLS denies access, you'll get empty results instead of 403
GET ${REST_API}/properties
// Returns: [] if user has no access to any properties
// Returns: [property1, property2] for properties user can access
```

---

**For Agents**: These examples cover every common API pattern. Use exact column names, enum values, and foreign key relationships as documented. All requests automatically respect RLS policies.